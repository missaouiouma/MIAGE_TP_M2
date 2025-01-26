import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4

from fastapi import HTTPException
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from models.models import User, Message, ChatResponse, Conversation
from services.mongo_service import MongoService

FUNCTION_DEFINITIONS = [
    {
        "name": "get_flights_info",
        "description": "Récupère des informations de vol entre deux villes (codes IATA) à une date donnée.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin_city": {"type": "string"},
                "destination_city": {"type": "string"},
                "departure_date": {"type": "string"}
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
        "name": "suggest_itinerary",
        "description": "Propose un itinéraire routier (voiture) à l'utilisateur en partant de sa ville de résidence.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "question": {"type": "string"}
            },
            "required": ["user_id", "question"]
        }
    },
    {
        "name": "get_restaurants_info",
        "description": "Récupère la liste des restaurants disponibles dans une ville donnée.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
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
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.flights_file = "./data/flights.csv"
        self.hotels_file = "./data/hotels.csv"
        self.restaurants_file = "./data/restaurants.csv"
        self.weather_file = "./data/weather.csv"

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

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user_data = await self.mongo_service.users_collection.find_one({"id": user_id})
        return User(**user_data) if user_data else None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username)
        return user if user and user.password == password else None

    async def get_flights_info(self, origin_city: str, destination_city: str, departure_date: Optional[str] = None) -> str:
        logging.info(f"Recherche de vols de {origin_city} à {destination_city}, date : {departure_date}")

        try:
            flights_df = pd.read_csv(self.flights_file)
            flights_filtered = flights_df[
                (flights_df['Origin_City'].str.lower() == origin_city.lower()) &
                (flights_df['Destination_City'].str.lower() == destination_city.lower())
            ]

            if departure_date:
                flights_filtered = flights_filtered[
                    flights_filtered['Departure_Date'] == departure_date
                ]

            if flights_filtered.empty:
                return f"Aucun vol disponible entre {origin_city} et {destination_city} à la date spécifiée."

            return "\n".join(
                f"Vol {row['Flight_Number']} ({row['Airline']}) | Départ : {row['Departure_Date']} {row['Departure_Time']} | Arrivée : {row['Arrival_Time']}"
                for _, row in flights_filtered.iterrows()
            )

        except Exception as e:
            logging.error(f"Erreur lors du chargement des vols : {str(e)}")
            return "Service des vols temporairement indisponible."

    async def get_hotels_info(self, city: str, stars: Optional[int] = None) -> str:
        logging.info(f"Recherche d'hôtels pour la ville : {city}, étoiles : {stars}")

        try:
            hotels_df = pd.read_csv(self.hotels_file)
            hotels_filtered = hotels_df[
                hotels_df['City'].str.lower() == city.lower()
            ]

            if stars:
                hotels_filtered = hotels_filtered[hotels_filtered['Stars'] == stars]

            if hotels_filtered.empty:
                return f"Aucun hôtel trouvé à {city}."

            return "\n\n".join(
                f"{row['Hotel_Name']} ({row['Stars']} étoiles)\nAdresse : {row['Address']}"
                for _, row in hotels_filtered.iterrows()
            )

        except Exception as e:
            logging.error(f"Erreur lors du chargement des hôtels : {str(e)}")
            return "Service hôtelier temporairement indisponible."

    async def get_restaurants_info(self, city: str, cuisine: Optional[str] = None, budget: Optional[str] = None, rating: Optional[float] = None) -> str:
        logging.info(f"Recherche de restaurants pour la ville : {city}, cuisine : {cuisine}, budget : {budget}, note minimale : {rating}")

        try:
            restaurants_df = pd.read_csv(self.restaurants_file)
            restaurants_filtered = restaurants_df[
                restaurants_df['City'].str.lower() == city.lower()
            ]

            if cuisine:
                restaurants_filtered = restaurants_filtered[restaurants_filtered['Cuisine'].str.lower() == cuisine.lower()]
            if budget:
                restaurants_filtered = restaurants_filtered[restaurants_filtered['Budget'] == budget]
            if rating:
                restaurants_filtered = restaurants_filtered[restaurants_filtered['Rating'] >= rating]

            if restaurants_filtered.empty:
                return f"Aucun restaurant trouvé à {city}."

            return "\n\n".join(
                f"{row['Restaurant']} ({row['Cuisine']}, Budget : {row['Budget']}, Note : {row['Rating']})"
                for _, row in restaurants_filtered.iterrows()
            )

        except Exception as e:
            logging.error(f"Erreur lors du chargement des restaurants : {str(e)}")
            return "Service des restaurants temporairement indisponible."

    async def get_weather_info(self, city: str, date: Optional[str] = None) -> str:
        logging.info(f"Recherche de la météo pour la ville : {city}, date : {date}")

        try:
            weather_df = pd.read_csv(self.weather_file)
            filtered_weather = weather_df[
                weather_df['City'].str.lower() == city.lower()
            ]

            if date:
                filtered_weather = filtered_weather[filtered_weather['Date'] == date]

            if filtered_weather.empty:
                return f"Aucune information météo trouvée pour {city} à la date spécifiée."

            return "\n".join(
                f"{row['Date']}: {row['Condition']}, Température : {row['Temperature']} °C"
                for _, row in filtered_weather.iterrows()
            )

        except Exception as e:
            logging.error(f"Erreur lors de la recherche météo : {str(e)}")
            return "Service météo temporairement indisponible."
    async def generate_response(self, message: str, session_id: str, user_id: str) -> ChatResponse:
        try:
            # 1) Préparer le contexte
            messages = [
    SystemMessage(
        content=(
            "Vous êtes un assistant de voyage. "
            "Utilisez les fonctions disponibles en cas de besoin ..."
        )
    )
]


            # 2) Récupérer l'historique en base
            conv_data = await self.mongo_service.conversations_collection.find_one({"session_id": session_id})
            if conv_data:
                for msg in conv_data.get("messages", []):
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    else:
                        messages.append(AIMessage(content=msg["content"]))

            # 3) **Ajouter le nouveau message de l'utilisateur AVANT l'appel au LLM**
            user_msg = Message(
                id=str(uuid4()),
                role="user",
                user_id=user_id,
                content=message,
                timestamp=datetime.utcnow()
            )
            # On l'ajoute aussi dans `messages` pour que le LLM puisse le lire
            messages.append(HumanMessage(content=message))

            # 4) Appeler le LLM avec la liste de tous les messages
            response = await self.chat_model.agenerate(
                [messages],
                functions=FUNCTION_DEFINITIONS,
                function_call="auto"
            )

            llm_message = response.generations[0][0].message
            response_text = ""
            suggestions = []

            # 5) Vérifier s'il y a un appel de fonction
            if function_call := llm_message.additional_kwargs.get("function_call"):
                fn_name = function_call["name"]
                args = json.loads(function_call.get("arguments", "{}"))
                logging.info(f"Fonction appelée : {fn_name} avec arguments {args}")

                if hasattr(self, fn_name):
                    response_text = await getattr(self, fn_name)(**args)
                else:
                    response_text = "Fonctionnalité non disponible."
            else:
                # Sinon, c'est juste une réponse texte
                response_text = llm_message.content

            # 6) Créer le message assistant et l'enregistrer en base
            assistant_msg = Message(
                id=str(uuid4()),
                role="assistant",
                user_id=user_id,
                content=response_text,
                timestamp=datetime.utcnow()
            )

            # Sauvegarder (upsert) les deux messages en base
            await self.save_message(session_id, user_id, user_msg)
            await self.save_message(session_id, user_id, assistant_msg)

            # 7) Retourner la réponse + suggestions
            return ChatResponse(
                response=response_text,
                suggestions=suggestions
            )

        except Exception as e:
            logging.error(f"Erreur génération : {str(e)}")
            return ChatResponse(
                response="Une erreur critique est survenue. Veuillez réessayer plus tard.",
                suggestions=["Réessayer", "Contacter le support"]
            )

        
    async def save_message(self, session_id: str, user_id: str, message: Message):
        try:
            await self.mongo_service.conversations_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message.dict()},
                    "$set": {"user_id": user_id, "updated_at": datetime.utcnow()}
                },
                upsert=True
            )
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du message : {str(e)}")