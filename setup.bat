@echo off
echo Installation de Salles libres ETS..

:: 1. Creation de l'environnement virtuel
echo Creation de l'environnement virtuel (venv)...
python -m venv venv

:: 2. Activation et installation des dependances
echo Installation des dependances...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install uvicorn fastapi python-multipart sqlalchemy pdfplumber loguru pydantic-settings

:: 3. Configuration du fichier .env
if not exist .env (
    echo Configuration du fichier .env par defaut...
    echo DATABASE_URL=sqlite:///./app.db > .env
)

:: 4. Creation des dossiers necessaires
if not exist data\uploads mkdir data\uploads
if not exist logs mkdir logs

echo Installation terminee avec succes !
echo Pour lancer le serveur, tapez : venv\Scripts\activate ^&^& uvicorn app.main:app --reload
pause
