"""
Modèles Pydantic pour la validation des données
Inclut les modèles du TP1 et les nouveaux modèles pour le TP2 adaptés à un assistant de voyage
"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


# ---- Modèles pour les requêtes de base ----
class ChatRequestTP1(BaseModel):
    """Requête de base pour une conversation sans contexte"""
    message: str

class ChatResponse(BaseModel):
    """Réponse standard de l'assistant"""
    response: str
    suggestions: Optional[List[str]] = None  # Ajouté pour inclure des suggestions de destinations

class ChatRequestWithContext(BaseModel):
    """Requête avec contexte de conversation"""
    message: str
    context: Optional[List[Dict[str, str]]] = []

# ---- Modèles avec gestion de session ----
class ChatRequestTP2(BaseModel):
    """Requête pour une conversation avec gestion de session"""
    message: str
    session_id: str  # Identifiant de session pour garder l'historique

class ChatMessage(BaseModel):
    """Structure d'un message individuel dans l'historique"""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: datetime
class ChatHistory(BaseModel):
    """Collection de messages formant une conversation"""
    messages: List[ChatMessage]

# ---- Modèles pour le résumé ----
class SummaryRequest(BaseModel):
    """Requête pour générer un résumé"""
    session_id: str  # Identifiant de session à résumer

class SummaryResponse(BaseModel):
    """Réponse contenant le résumé de la session"""
    full_summary: str  # Résumé complet de la session
    bullet_points: List[str]  # Points principaux extraits de la session
    one_liner: str  # Résumé en une seule ligne
