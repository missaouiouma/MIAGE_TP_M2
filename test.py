import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongo_connection():
    # Remplacez par votre URI MongoDB
    uri = "mongodb+srv://missaouioumaymaaa:MissaOuma%402209%21@aivoyage.kpfm6.mongodb.net/"
    client = AsyncIOMotorClient(uri)

    try:
        print("Connexion à MongoDB...")
        # Vérifiez si la base de données est accessible
        db = client["AIvoyage"]
        collections = await db.list_collection_names()
        print("Collections disponibles :", collections)
        print("Connexion réussie à MongoDB !")
    except Exception as e:
        print("Erreur de connexion :", e)

# Exécuter le test
asyncio.run(test_mongo_connection())
