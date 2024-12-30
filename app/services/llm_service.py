from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from services.mongo_service import MongoService
from typing import List, Dict, Optional
import os
import logging

class LLMService:
    """
    Service LLM avec intégration MongoDB et gestion améliorée.
    """

    def __init__(self):
        # Vérification de la clé API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY n'est pas définie")

        # Configuration du modèle OpenAI
        self.llm = ChatOpenAI(
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
            model_name=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=api_key
        )

        # Service MongoDB
        self.mongo_service = MongoService()

        # Configurer le logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("LLMService initialisé avec succès.")

    async def generate_response(self, message: str, session_id: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Génère une réponse et sauvegarde dans MongoDB.
        Si un contexte est fourni, il sera utilisé pour construire les messages.
        """
        try:
            # Construire les messages en fonction du contexte ou de l'historique
            messages = [SystemMessage(content="Vous êtes un assistant utile et concis.")]
            if context:
                for msg in context:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            else:
                # Récupérer l'historique de la session depuis MongoDB si aucun contexte explicite n'est fourni
                history = await self.mongo_service.get_conversation_history(session_id)
                for msg in history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

            # Ajouter le nouveau message
            messages.append(HumanMessage(content=message))

            # Génération de la réponse
            response = await self.llm.agenerate([messages])
            response_text = response.generations[0][0].text

            # Sauvegarder les messages dans MongoDB
            await self.mongo_service.save_message(session_id, "user", message)
            await self.mongo_service.save_message(session_id, "assistant", response_text)

            return response_text

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de la réponse : {e}")
            raise

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Récupère l'historique depuis MongoDB pour une session donnée.
        """
        try:
            history = await self.mongo_service.get_conversation_history(session_id)
            self.logger.info(f"Historique récupéré pour la session {session_id}.")
            return history
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'historique : {e}")
            raise

    async def summarize_conversation(self, session_id: str) -> str:
        """
        Génère un résumé de la conversation pour une session donnée.
        """
        try:
            # Récupération de l'historique
            history = await self.mongo_service.get_conversation_history(session_id)
            if not history:
                return "Aucun message disponible pour cette session."

            # Conversion des messages en texte brut
            conversation_text = "\n".join(
                f"{msg['role']}: {msg['content']}" for msg in history
            )

            # Génération du résumé
            summary_prompt = [
                SystemMessage(content="Veuillez résumer la conversation suivante :"),
                HumanMessage(content=conversation_text),
            ]
            summary = await self.llm.agenerate([summary_prompt])
            summary_text = summary.generations[0][0].text

            self.logger.info(f"Résumé généré pour la session {session_id}.")
            return summary_text

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du résumé : {e}")
            raise
