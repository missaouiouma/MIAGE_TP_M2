import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """
    Classe de configuration pour MongoDB.
    Charge les variables depuis le fichier .env ou utilise des valeurs par défaut.
    """
    mongodb_uri = os.getenv("MONGODB_URI", "")  # URI MongoDB (obligatoire)
    database_name = os.getenv("DATABASE_NAME", "default_db")  # Nom de la base de données
    collection_name = os.getenv("COLLECTION_NAME", "default_collection")  # Nom de la collection

    @staticmethod
    def validate():
        """
        Valide que les paramètres essentiels sont définis.
        """
        if not Config.mongodb_uri:
            raise ValueError("La variable d'environnement MONGODB_URI n'est pas définie.")
        if not Config.database_name:
            raise ValueError("La variable d'environnement DATABASE_NAME n'est pas définie.")
        if not Config.collection_name:
            raise ValueError("La variable d'environnement COLLECTION_NAME n'est pas définie.")

# Validation des paramètres
Config.validate()
