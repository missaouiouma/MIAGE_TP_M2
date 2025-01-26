from fastapi import APIRouter, HTTPException
from typing import List
from services.llm_service import LLMService
from models.models import User, Message, ChatResponse, RegisterRequest, LoginRequest, AskRequest

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
    Authentifie un utilisateur (sans hashage).
    """
    try:
        # Rechercher l'utilisateur dans la base de données
        user = await llm_service.get_user_by_username(request.username)
        if not user:
            raise HTTPException(status_code=401, detail="Nom d'utilisateur incorrect")

        # Vérification du mot de passe en clair
        if request.password != user.password:
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        # Retourner les informations essentielles de l'utilisateur
        return {
            "user_id": user.id,
            "username": user.username,
            "message": "Connexion réussie"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la connexion : {str(e)}")


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: AskRequest):
    """
    Permet à l'utilisateur de poser une question.
    """
    try:
        session_id = f"{request.user_id}_session"
        response = await llm_service.generate_response(request.question, session_id, request.user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@router.get("/users/{user_id}/messages", response_model=List[Message])
async def get_user_messages(user_id: str):
    """
    Récupère tous les messages pour un utilisateur donné.
    """
    try:
        messages = await llm_service.get_user_messages(user_id)
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des messages : {str(e)}")
