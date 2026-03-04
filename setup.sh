#!/bin/bash

echo "🚀 Installation de ETS Room Finder PRO..."

# 1. Création de l'environnement virtuel
echo "📦 Création de l'environnement virtuel (venv)..."
python3 -m venv venv

# 2. Activation et installation des dépendances
echo "📥 Installation des dépendances..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn fastapi python-multipart sqlalchemy pdfplumber loguru pydantic-settings

# 3. Configuration du fichier .env
if [ ! -f .env ]; then
    echo "⚙️ Configuration du fichier .env par défaut..."
    echo "DATABASE_URL=sqlite:///./app.db" > .env
fi

# 4. Création des dossiers nécessaires
mkdir -p data/uploads logs

echo "✅ Installation terminée avec succès !"
echo "👉 Pour lancer le serveur, tapez : source venv/bin/activate && uvicorn app.main:app --reload"
