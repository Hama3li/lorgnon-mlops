# Étape 1 : Image de base
FROM python:3.8-slim

# Étape 2 : Définir le dossier de travail
WORKDIR /app

# Étape 3 : Copier les fichiers nécessaires
COPY requirements.txt .

# Étape 4 : Installer les dépendances
RUN pip install --upgrade pip && pip install -r requirements.txt

# Étape 5 : Copier le reste du projet (modèle, code, DB, etc.)
COPY . .

# Étape 6 : Initialiser la base de données SQLite
RUN python init_db.py

# Étape 7 : Exposer le port de l’API
EXPOSE 8000

# Étape 8 : Commande pour lancer le serveur FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
