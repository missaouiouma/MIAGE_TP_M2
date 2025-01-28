# Projet TP MIAGE M2 - Agent Conversationnel - TravelAI 

## Structure du Projet

```
C:.
├───api/                    # Backend du projet: Gestion des routes et endpoints de l'API
│   ├───endpoints/         # Endpoints spécifiques par fonctionnalité
│   │   └───chat.py       # Endpoint pour les fonctionnalités de chat
│   └───router.py         # Router principal regroupant tous les endpoints
├───core/                  # Configuration et éléments centraux de l'application
├───models/               # Modèles de données Pydantic
│   |                     # Modèles pour les requêtes/réponses de chat
|   └───models.py  
├───services/            # Services métier
│   └───llm_service.py   # Service d'interaction avec le LLM
|   └───memory.py 
|   └───mongo_service.py 

├───utils/               # Utilitaires et helpers
└───main.py   # Point d'entrée de l'application
├───chatbot-frontend/
   └──   src/
      ├── pages/
      │   ├── ChatbotPage.jsx
      │   ├── LoginPage.jsx
      │   ├── RegisterPage.jsx
      │  
      ├── api/
      │   └── api.js
      └── App.jsx




```

## Installation et Configuration

### Prérequis
- Python 3.11+ 
- Visual Studio Code avec l'extension Python
- la clé OpenAI 
### Installation

**Créer l'environnement virtuel**
```bash
python -m venv venv
```

**Activer l'environnement virtuel**
- Windows :
```bash
.\venv\Scripts\activate
```
- macOS/Linux :
```bash
source venv/bin/activate
```

**Installer les dépendances**
```bash
pip install -r requirements.txt
cd chatbot-frontend
npm install axios @headlessui/react @heroicons/react tailwindcss
npm install -D @tailwindcss/forms postcss autoprefixer
```

**Configurer la clé API OpenAI**
Créer un fichier `.env` à la racine du projet :
```
OPENAI_API_KEY=votre-clé-api-openai
```
**Configurer de MongoDB**
 1. Créez un compte gratuit sur MongoDB Atlas (https://cloud.mongodb.com/v2/)
 2. Créez un cluster gratuit (M0)
 3. Configurez les accès réseau (whitelist votre IP)
 4. Créez un u lisateur de base de données
 5. Récupérez votre chaîne de connexion
dans le même fichier `.env` : ajouter MONGODB_URI , DATABASE_NAME et COLLECTION_NAME
 
```

## tester le backend

1. Ouvrir le projet dans VS Code
2. Aller dans la section "Run and Debug" (Ctrl + Shift + D)
3. Sélectionner la configuration "Python: FastAPI"
4. Appuyer sur F5 ou cliquer sur le bouton Play
5. Démarrer Swagger : http://127.0.0.1:8000/docs


## tester le backend et le front 
1. Aller dans la section "Run and Debug" (Ctrl + Shift + D)
2. Sélectionner la configuration "Python: FastAPI"
3. Appuyer sur F5 ou cliquer sur le bouton Play
4. cd chatbot-frontend lancer npm start 