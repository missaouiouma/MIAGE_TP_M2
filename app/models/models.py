from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# ---- Modèles de base ----
class Message(BaseModel):
    id: str = Field(..., description="Identifiant unique du message.")
    role: Literal["user", "assistant"]  # Le rôle du message
    content: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Date et heure du message.")

class Conversation(BaseModel):
    session_id: str = Field(..., description="Identifiant unique de la session.")
    messages: List[Message] = Field(default=[], description="Liste des messages de la conversation.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création de la conversation.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Dernière mise à jour de la conversation.")
    is_active: bool = Field(default=True, description="Indique si la session est active.")

# ---- Modèles utilisateurs ----
class User(BaseModel):
    id: str
    username: str
    password: str
    age: int  
    loisirs: List[str] 
    pays_de_naissance: str  
    pays_de_residence: str
    ville_de_residence: str  

# ---- Modèles pour les requêtes et réponses ----
class ChatRequestWithContext(BaseModel):
    message: str = Field(..., description="Message envoyé par l'utilisateur.")
    context: Optional[List[Message]] = Field(default=[], description="Contexte de la conversation.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Réponse générée par l'assistant.")
    suggestions: Optional[List[str]] = Field(default=None, description="Suggestions fournies par l'assistant.")

class SummaryRequest(BaseModel):
    session_id: str = Field(..., description="Identifiant de la session à résumer.")

class SummaryResponse(BaseModel):
    full_summary: str = Field(..., description="Résumé complet de la session.")
    bullet_points: List[str] = Field(..., description="Points principaux extraits de la session.")
    one_liner: str = Field(..., description="Résumé en une seule ligne.")

class RegisterRequest(BaseModel):
    username: str
    password: str
    age: int
    loisirs: List[str]
    pays_de_naissance: str
    pays_de_residence: str
    ville_de_residence: str

class LoginRequest(BaseModel):
    username: str 
    password: str 

class AskRequest(BaseModel):
    user_id: str
    question: str
