import os
import json
import logging
import pandas as pd
from datetime import datetime
from datetime import timedelta
from typing import List, Dict, Optional
from uuid import uuid4

from fastapi import HTTPException
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.schema import FunctionMessage
from models.models import User, Message, ChatResponse, Conversation
from services.mongo_service import MongoService
from datetime import datetime
from pytz import timezone

FUNCTION_DEFINITIONS = [
    {
        "name": "get_flights_info",
        "description": "Récupère des informations de vol entre deux villes (noms en français) pour un mois ou une date spécifique.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin_city": {"type": "string", "description": "Nom complet de la ville de départ (ex: 'Mexico City')"},
                "destination_city": {"type": "string", "description": "Nom complet de la ville d'arrivée (ex: 'Dubai')"},
                "departure_date": {"type": "string", "description": "Date au format YYYY-MM ou YYYY-MM-DD (facultatif)"}
            },
            "required": ["origin_city", "destination_city"]
        }
    },
    {
        "name": "get_hotels_info",
        "description": "Récupère la liste des hôtels disponibles dans une ville donnée avec filtrage par étoiles.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "stars": {"type": "number", "description": "Nombre d'étoiles souhaité (1-5)"}
            },
            "required": ["city"]
        }
    },
    {
    "name": "get_restaurants_info",
    "description": "Récupère la liste des restaurants disponibles dans une ville donnée.",
    "parameters": {
        "type": "object",
        "properties": {
        "city": {"type": "string", "description": "Nom de la ville"},
        "cuisine": {"type": "string", "description": "Type de cuisine (italienne, japonaise, etc.)"},
        "budget": {"type": "string", "description": "Budget approximatif ($, $$, $$$)"},
        "rating": {"type": "number", "description": "Note minimale (1-5)"}
        },
        "required": ["city"]
    }
    },

    {
        "name": "get_weather_info",
        "description": "Récupère les informations météorologiques pour une ville donnée.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "date": {"type": "string", "description": "Date pour la météo (facultative)."}
            },
            "required": ["city"]
        }
    }
]

class LLMService:
    def __init__(self):
        self.mongo_service = MongoService()
        self.chat_model = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o"       
        )
    async def initialize_indexes(self):
        await self.mongo_service.users_collection.create_index("username", unique=True)
        await self.mongo_service.conversations_collection.create_index("session_id")

    async def get_user_by_username(self, username: str) -> Optional[User]:
        user_data = await self.mongo_service.users_collection.find_one({"username": username})
        return User(**user_data) if user_data else None

    async def create_user(self, username: str, password: str, age: int, loisirs: List[str],
                          pays_de_naissance: str, pays_de_residence: str, ville_de_residence: str) -> User:
        if await self.get_user_by_username(username):
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

        new_user = User(
            id=f"user_{uuid4()}",
            username=username,
            password=password,
            age=age,
            loisirs=loisirs,
            pays_de_naissance=pays_de_naissance,
            pays_de_residence=pays_de_residence,
            ville_de_residence=ville_de_residence
        )
        await self.mongo_service.users_collection.insert_one(new_user.dict())
        return new_user
    
    async def create_new_session(self, user_id: str) -> str:
        """
        Crée une nouvelle session pour l'utilisateur et marque les sessions existantes comme inactives.
        """
        try:
            # Marquer les sessions existantes comme inactives
            await self.mongo_service.conversations_collection.update_many(
                {"user_id": user_id, "is_active": True},
                {"$set": {"is_active": False}}
            )

            # Créer une nouvelle session
            session_id = f"{user_id}_session_{uuid4()}"
            new_session = {
                "session_id": session_id,
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,  # Nouvelle session active
            }
            await self.mongo_service.conversations_collection.insert_one(new_session)

            return session_id
        except Exception as e:
            logging.error(f"Erreur lors de la création d'une nouvelle session pour l'utilisateur {user_id} : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la création d'une nouvelle session.")



    
    async def get_conversations_by_user(self, user_id: str) -> List[Conversation]:
        """
        Récupère toutes les conversations d'un utilisateur.
        """
        conversations = await self.mongo_service.conversations_collection.find({"user_id": user_id}).to_list(length=None)
        return [Conversation(**conv) for conv in conversations]

    async def generate_response(self, message: str, session_id: str, user_id: str) -> ChatResponse:
        try:
            logging.info(f"Début de `generate_response` pour le message: {message}, session_id: {session_id}, user_id: {user_id}")

            # Initialisation des messages avec instructions pour le LLM
            messages = [
                SystemMessage(content=(
                    "Vous êtes un assistant intelligent spécialisé dans la recherche d'informations pratiques (hôtels, restaurants, vols, météo). "
                    "Utilisez toujours les fonctions pour fournir des informations précises, puis reformulez de manière claire pour l'utilisateur."
                ))
            ]

            # Récupération de la conversation existante
            conv_data = await self.mongo_service.conversations_collection.find_one({"session_id": session_id})
            if conv_data:
                for msg in conv_data.get("messages", []):
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

            # Ajout du message utilisateur actuel
            user_msg = HumanMessage(content=message)
            messages.append(user_msg)

            # Appel initial au LLM
            response = await self.chat_model.agenerate(
                [messages],
                functions=FUNCTION_DEFINITIONS,
                function_call="auto"
            )
            llm_message = response.generations[0][0].message
            logging.info(f"Réponse brute du LLM : {llm_message}")

            # Si un `function_call` est détecté
            function_call = llm_message.additional_kwargs.get("function_call")
            if function_call:
                fn_name = function_call["name"]
                args = json.loads(function_call.get("arguments", "{}"))

                if hasattr(self, fn_name):
                    try:
                        logging.info(f"Appel de la fonction `{fn_name}` avec arguments: {args}")
                        function_response = await getattr(self, fn_name)(**args)
                        logging.info(f"Réponse de la fonction `{fn_name}`: {function_response}")

                        if "Aucun" in function_response:
                            final_message = function_response  # Pas besoin de reformuler si aucun résultat
                        else:
                            # Ajouter les résultats pour reformulation
                            messages.append(FunctionMessage(
                                name=fn_name, 
                                content=function_response,
                            ))                            
                            refined_response = await self.chat_model.agenerate([messages])

                            # Si la reformulation est vide, utilise les données brutes formatées
                            if refined_response.generations[0][0].message.content.strip():
                                final_message = refined_response.generations[0][0].message.content
                            else:
                                logging.warning("Reformulation vide. Utilisation des résultats bruts.")
                                final_message = f"Voici les résultats trouvés :\n{function_response}"

                    except Exception as e:
                        logging.error(f"Erreur lors de l'appel de la fonction `{fn_name}` : {str(e)}")
                        final_message = "Une erreur est survenue lors de l'obtention des données. Veuillez réessayer."
                else:
                    logging.warning(f"Fonction `{fn_name}` non implémentée.")
                    final_message = "Désolé, cette fonctionnalité n'est pas encore disponible."

            else:
                # Si aucun function_call détecté
                logging.warning("Aucun function_call détecté.")
                final_message = llm_message.content or "Je n'ai pas compris votre demande. Pouvez-vous préciser ?"

            # Sauvegarde des messages dans la base de données
            assistant_msg = AIMessage(content=final_message)
            await self.save_message(session_id, user_id, user_msg)
            await self.save_message(session_id, user_id, assistant_msg)

            return ChatResponse(response=final_message)

        except Exception as e:
            logging.error(f"Erreur dans `generate_response` : {str(e)}")
            return ChatResponse(
                response="Une erreur critique est survenue. Veuillez réessayer plus tard.",
                suggestions=["Réessayer", "Contacter le support"]
            )

    async def save_message(self, session_id: str, user_id: str, message: Message):
        """
        Sauvegarde un message dans la session correspondante.
        """
        try:
            # Vérifier si la session existe
            session = await self.mongo_service.conversations_collection.find_one({"session_id": session_id})
            if not session:
                raise HTTPException(status_code=404, detail="Session introuvable.")

            # Ajouter le message à la session
            await self.mongo_service.conversations_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message.dict()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du message pour la session {session_id} : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde du message.")



    async def get_flights_info(self, origin_city: str, destination_city: str, departure_date: Optional[str] = None) -> str:
        logging.info(f"Recherche de vols de {origin_city} à {destination_city}, date : {departure_date}")

        try:
            query = {
                "ville_dorigine": origin_city,
                "ville_de_destination": destination_city
            }

            if departure_date:
                try:
                    # Convertir "2024-03" en une plage de dates
                    start_date = datetime.strptime(departure_date, "%Y-%m")
                    # Calculer la fin du mois
                    if start_date.month == 12:
                        end_date = datetime(start_date.year + 1, 1, 1)
                    else:
                        end_date = datetime(start_date.year, start_date.month + 1, 1)

                    query["date_de_depart"] = {
                        "$gte": start_date,
                        "$lt": end_date
                    }
                except ValueError:
                    logging.error("Format de date invalide. Utilisez 'YYYY-MM'.")
                    return "Format de date invalide. Utilisez 'YYYY-MM'."

            # Utilisation correcte de to_list() pour récupérer les résultats
            flights = await self.mongo_service.db["vols"].find(query).to_list(length=None)

            if not flights:
                return f"Aucun vol disponible entre {origin_city} et {destination_city} à la date spécifiée."

            # Formater les résultats des vols
            return "\n".join([
                f"Vol {flight.get('numero_de_vol', 'N/A')} ({flight.get('compagnie_aerienne', 'N/A')}) | "
                f"Départ : {flight.get('date_de_depart', 'N/A')} {flight.get('heure_de_depart', 'N/A')} | "
                f"Arrivée : {flight.get('heure_arrivee', 'N/A')}"
                for flight in flights
            ])

        except Exception as e:
            logging.error(f"Erreur lors du chargement des vols : {str(e)}")
            return "Service des vols temporairement indisponible."



    async def get_hotels_info(self, city: str, stars: Optional[int] = None) -> str:
        logging.info(f"Recherche d'hôtels pour la ville : {city}, étoiles : {stars}")

        try:
            query = {"ville": city}

            if stars:
                query["etoiles"] = stars

            # Utilisation correcte de to_list()
            hotels = await self.mongo_service.db["hotels"].find(query).to_list(length=None)

            if not hotels:
                return f"Aucun hôtel trouvé à {city}."

            return "\n\n".join([
                f"{hotel.get('nom_de_lhôtel', 'N/A')} ({hotel.get('etoiles', 'N/A')} étoiles)\n"
                f"Adresse : {hotel.get('adresse', 'N/A')}\n"
                f"Date de disponibilité : {hotel.get('date_de_disponibilite', 'N/A')}"
                for hotel in hotels
            ])

        except Exception as e:
            logging.error(f"Erreur lors du chargement des hôtels : {str(e)}")
            return "Service hôtelier temporairement indisponible."

    async def get_restaurants_info(self, city: str, cuisine: Optional[str] = None, budget: Optional[str] = None, rating: Optional[float] = None) -> str:
        logging.info(f"Recherche de restaurants pour la ville : {city}, cuisine : {cuisine}, budget : {budget}, note minimale : {rating}")

        try:
            query = {"ville": city}

            if cuisine:
                query["cuisine"] = {"$regex": cuisine, "$options": "i"}  
            if budget:
                query["budget"] = budget
            if rating:
                query["evaluation"] = {"$gte": rating}

            logging.debug(f"Requête MongoDB : {query}")

            # Utilisation correcte de to_list()
            restaurants = await self.mongo_service.db["restaurants"].find(query).to_list(length=None)

            logging.debug(f"Résultats MongoDB : {restaurants}")

            if not restaurants:
                return f"Aucun restaurant trouvé à {city}."

            # Construire une liste formatée avec des sauts de ligne bien placés
            result = []
            for restaurant in restaurants:
                    result.append(
                        f"Nom: {restaurant.get('nom_du_restaurant', 'N/A')}, "
                        f"Cuisine: {restaurant.get('cuisine', 'N/A')}, "
                        f"Budget: {restaurant.get('budget', 'N/A')}, "
                        f"Note: {restaurant.get('evaluation', 'N/A')}, "
                        f"Adresse: {restaurant.get('adresse', 'N/A')}"
                    )

            return "; ".join(result)  # Les résultats sont séparés par "; " pour être plus lisibles.


        except Exception as e:
            logging.error(f"Erreur lors du chargement des restaurants : {str(e)}")
            return "Service des restaurants temporairement indisponible."




    async def get_weather_info(self, city: str, date: Optional[str] = None) -> str:
        logging.info(f"Recherche de la météo pour la ville : {city}, date : {date}")

        try:
            query = {"ville": city}

            if date:
                try:
                    # Conversion de la chaîne de date en objet datetime (en UTC)
                    date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone('UTC'))
                    query["date"] = date_obj
                except ValueError:
                    logging.error(f"Format de date invalide : {date}")
                    return "Format de date invalide. Utilisez le format YYYY-MM-DD."

            # Utilisation correcte de to_list()
            weather = await self.mongo_service.db["climat"].find(query).to_list(length=None)

            if not weather:
                return f"Aucune information météo trouvée pour {city} à la date spécifiée."

            return "\n".join([
                f"{entry.get('date', 'N/A')}: {entry.get('condition', 'N/A')}, "
                f"Température : {entry.get('temperature_(°c)', 'N/A')} °C"
                for entry in weather
            ])

        except Exception as e:
            logging.error(f"Erreur lors de la recherche météo : {str(e)}")
            return "Service météo temporairement indisponible."