@echo off
echo Lancement de Salles libres ETS...

:: 1. Activer l'environnement virtuel
call venv\Scripts\activate

:: 2. Lancer le serveur en ARRIERE-PLAN pour ne pas bloquer le script
start /b uvicorn app.main:app --reload

:: 3. Attendre 3 secondes que le serveur demarre
timeout /t 3 /nobreak > nul

:: 4. Ouvrir le navigateur
start "" "http://localhost:8000"

:: 5. Garder la fenetre ouverte pour voir les logs
echo.
echo Le serveur est en ligne ! Gardez cette fenetre ouverte.
echo Appuyez sur Ctrl+C pour arreter.
echo.
pause
