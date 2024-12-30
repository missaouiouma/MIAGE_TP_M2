from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Dict
from core.config import Config  # Import de la configuration
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)

class MongoService:
    """
    Service pour interagir avec MongoDB (sauvegarde, récupération, suppression de données).
    """
    def __init__(self):
        # Initialisation de la connexion MongoDB
        self.client = AsyncIOMotorClient(Config.mongodb_uri)
        self.db = self.client[Config.database_name]
        self.conversations = self.db[Config.collection_name]
        logging.info("Connexion à MongoDB établie.")

    async def save_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Sauvegarde un message dans une conversation.
        :param session_id: ID de la session.
        :param role: Rôle de l'expéditeur (user/assistant).
        :param content: Contenu du message.
        :return: True si la sauvegarde a réussi, False sinon.
        """
        try:
            message = {"role": role, "content": content, "timestamp": datetime.utcnow()}
            result = await self.conversations.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()},
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            logging.info(f"Message sauvegardé pour la session {session_id}.")
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du message : {e}")
            return False

    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Récupère l'historique des messages d'une conversation.
        :param session_id: ID de la session.
        :return: Liste des messages ou liste vide si aucune conversation n'existe.
        """
        try:
            conversation = await self.conversations.find_one({"session_id": session_id})
            if conversation:
                logging.info(f"Historique trouvé pour la session {session_id}.")
                return conversation.get("messages", [])
            logging.warning(f"Aucun historique trouvé pour la session {session_id}.")
            return []
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'historique : {e}")
            return []

    async def delete_conversation(self, session_id: str) -> bool:
        """
        Supprime une conversation.
        :param session_id: ID de la session.
        :return: True si la suppression a réussi, False sinon.
        """
        try:
            result = await self.conversations.delete_one({"session_id": session_id})
            if result.deleted_count > 0:
                logging.info(f"Conversation supprimée pour la session {session_id}.")
                return True
            logging.warning(f"Aucune conversation trouvée pour la session {session_id}.")
            return False
        except Exception as e:
            logging.error(f"Erreur lors de la suppression de la conversation : {e}")
            return False

    async def get_all_sessions(self) -> List[str]:
        """
        Récupère tous les IDs de session existants.
        :return: Liste des IDs de session.
        """
        try:
            cursor = self.conversations.find({}, {"session_id": 1})
            sessions = await cursor.to_list(length=None)
            logging.info(f"{len(sessions)} sessions récupérées.")
            return [session["session_id"] for session in sessions]
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des sessions : {e}")
            return []
