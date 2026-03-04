#!/bin/bash

echo "Lancement de Salles libres ÉTS..."

# 1. Activer l'environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Erreur : Dossier 'venv' non trouvé. Lancez d'abord ./setup.sh"
    exit 1
fi

# 2. Lancer le serveur en arrière-plan
uvicorn app.main:app --reload &
SERVER_PID=$!

# 3. Attendre que le serveur démarre
echo "Attente du démarrage du serveur..."
sleep 3

# 4. Ouvrir le navigateur (Mac ou Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:8000"
else
    xdg-open "http://localhost:8000" 2>/dev/null || echo "Ouvrez http://localhost:8000 dans votre navigateur."
fi

echo ""
echo "Le serveur est en ligne ! Gardez ce terminal ouvert."
echo "Appuyez sur Ctrl+C pour arrêter."
echo ""

# 5. Attendre la fin du processus
wait $SERVER_PID
