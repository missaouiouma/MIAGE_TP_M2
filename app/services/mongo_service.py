from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Dict, Optional
from models.models import User, Message, Conversation
import logging
import os

# Configurer le logging
logging.basicConfig(level=logging.INFO)

class MongoService:
    """
    Service pour interagir avec MongoDB (utilisateurs et conversations).
    """

    def __init__(self):
        # Initialisation de la connexion MongoDB
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("DATABASE_NAME")]
        self.users_collection = self.db["users"]
        self.conversations_collection = self.db["conversations"]

    # ---- Méthodes pour les utilisateurs ----

    async def add_user(self, username: str, hashed_password: str) -> User:
        """
        Ajoute un nouvel utilisateur.
        """
        # Vérifier si l'utilisateur existe déjà
        existing_user = await self.users_collection.find_one({"username": username})
        if existing_user:
            raise ValueError(f"L'utilisateur {username} existe déjà.")

        # Créer un utilisateur
        user = User(
            id=str(await self.users_collection.count_documents({}) + 1),
            username=username,
            hashed_password=hashed_password
        )
        await self.users_collection.insert_one(user.dict())
        logging.info(f"Utilisateur {username} ajouté à la base de données.")
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        """
        user_data = await self.users_collection.find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.
        """
        user_data = await self.users_collection.find_one({"id": user_id})
        if user_data:
            return User(**user_data)
        return None

    async def set_preferences(self, user_id: str, preferences: Dict) -> None:
        """
        Enregistre les préférences de l'utilisateur dans MongoDB.
        """
        await self.users_collection.update_one(
            {"id": user_id},
            {"$set": {"preferences": preferences}},
            upsert=True
        )
        logging.info(f"Préférences mises à jour pour l'utilisateur {user_id}.")

    async def get_preferences(self, user_id: str) -> Optional[Dict]:
        """
        Récupère les préférences de l'utilisateur.
        """
        user = await self.users_collection.find_one({"id": user_id}, {"_id": 0, "preferences": 1})
        if user and "preferences" in user:
            return user["preferences"]
        return None

    # ---- Méthodes pour les conversations ----

    async def create_conversation(self, user_id: str) -> Conversation:
        """
        Crée une nouvelle conversation pour un utilisateur.
        """
        conversation = Conversation(
            id=str(await self.conversations_collection.count_documents({}) + 1),
            user_id=user_id,
            messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.conversations_collection.insert_one(conversation.dict())
        logging.info(f"Conversation créée pour l'utilisateur {user_id}.")
        return conversation

    async def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> None:
        """
        Ajoute un message à une conversation existante.
        """
        message = Message(role=role, content=content, timestamp=datetime.utcnow())
        await self.conversations_collection.update_one(
            {"id": conversation_id},
            {"$push": {"messages": message.dict()}, "$set": {"updated_at": datetime.utcnow()}}
        )
        logging.info(f"Message ajouté à la conversation {conversation_id}.")

    async def get_conversations_by_user(self, user_id: str) -> List[Conversation]:
        """
        Récupère toutes les conversations d'un utilisateur.
        """
        conversations_cursor = self.conversations_collection.find({"user_id": user_id})
        conversations = []
        async for conversation in conversations_cursor:
            conversations.append(Conversation(**conversation))
        return conversations

    async def get_conversation_history(self, conversation_id: str) -> Optional[Conversation]:
        """
        Récupère l'historique d'une conversation spécifique.
        """
        conversation_data = await self.conversations_collection.find_one({"id": conversation_id})
        if conversation_data:
            return Conversation(**conversation_data)
        return None

    async def summarize_conversation(self, conversation_id: str) -> str:
        """
        Résume une conversation spécifique.
        """
        conversation = await self.get_conversation_history(conversation_id)
        if not conversation:
            return "Aucune conversation trouvée."

        # Créer un résumé simple
        summary = f"Résumé de la conversation {conversation.id} :\n"
        for msg in conversation.messages:
            summary += f"{msg['role']}: {msg['content']}\n"

        logging.info(f"Résumé généré pour la conversation {conversation_id}.")
        return summary
