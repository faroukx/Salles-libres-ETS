#!/bin/bash
# Ajouter le répertoire courant au PYTHONPATH pour que 'app' soit reconnu comme un module
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Lancer l'application avec Gunicorn et le worker Uvicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
