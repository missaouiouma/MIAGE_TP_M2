from fastapi import APIRouter, HTTPException
from typing import List
from services.llm_service import LLMService
from models.models import User, Message, ChatResponse, RegisterRequest, LoginRequest, AskRequest, SessionResponse
from typing import Optional
import logging 
from datetime import datetime
router = APIRouter()
llm_service = LLMService()

@router.post("/register", response_model=User)
async def register_user(request: RegisterRequest):
    """
    Crée un nouvel utilisateur avec des informations obligatoires.
    """
    try:
        existing_user = await llm_service.get_user_by_username(request.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

        # Crée un nouvel utilisateur avec les champs obligatoires
        new_user = await llm_service.create_user(
            username=request.username,
            password=request.password,
            age=request.age,
            loisirs=request.loisirs,
            pays_de_naissance=request.pays_de_naissance,
            pays_de_residence=request.pays_de_residence,
            ville_de_residence=request.ville_de_residence,
        )
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'utilisateur : {str(e)}")


@router.post("/login")
async def login_user(request: LoginRequest):
    """
    Authentifie un utilisateur et crée une nouvelle session.
    """
    try:
        # Rechercher l'utilisateur dans la base de données
        user = await llm_service.get_user_by_username(request.username)
        if not user:
            raise HTTPException(status_code=401, detail="Nom d'utilisateur incorrect")

        # Vérification du mot de passe en clair
        if request.password != user.password:
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        # Créer une nouvelle session pour l'utilisateur
        session_id = await llm_service.create_new_session(user.id)

        # Retourner les informations essentielles de l'utilisateur et de la session
        return {
            "user_id": user.id,
            "username": user.username,
            "session_id": session_id,
            "message": "Connexion réussie"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la connexion : {str(e)}")

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: AskRequest):
    """
    Permet à l'utilisateur de poser une question. Crée une nouvelle session si aucune session active n'existe.
    """
    try:
        # Récupérer une session active ou en créer une nouvelle
        session = await llm_service.mongo_service.conversations_collection.find_one(
            {"user_id": request.user_id, "is_active": True}
        )

        if not session:
            # Créer une nouvelle session si aucune n'existe
            session_id = await llm_service.create_new_session(request.user_id)
        else:
            session_id = session["session_id"]

        # Appeler la génération de réponse
        response = await llm_service.generate_response(request.question, session_id, request.user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")




@router.get("/users/{user_id}/messages", response_model=List[Message])
async def get_user_messages(user_id: str, session_id: Optional[str] = None):
    try:
        query = {"user_id": user_id}
        if session_id:
            query["session_id"] = session_id

        # Trouver UNE conversation (session) spécifique
        conversation = await llm_service.mongo_service.conversations_collection.find_one(query)

        if not conversation:
            return []

        # Extraire les messages de cette session
        messages = conversation.get("messages", [])
        return [Message(**msg) for msg in messages]

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des messages : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")

    
@router.get("/users/{user_id}/sessions", response_model=List[SessionResponse])
async def get_user_sessions(user_id: str):
    """
    Récupère toutes les sessions pour un utilisateur donné.
    """
    try:
        sessions = await llm_service.mongo_service.conversations_collection.find({"user_id": user_id}).to_list(length=None)
        if not sessions:
            return []

        return [
            SessionResponse(
                session_id=session["session_id"],
                created_at=session.get("created_at", datetime.utcnow()),
                updated_at=session.get("updated_at", datetime.utcnow()),
                is_active=session.get("is_active", True),
            )
            for session in sessions
        ]
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des sessions pour l'utilisateur {user_id} : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")
