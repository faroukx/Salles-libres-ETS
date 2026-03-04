from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base
from loguru import logger
import time
import os

# Création automatique des tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CONFIGURATION CORS (INDISPENSABLE POUR L'UPLOAD DEPUIS LE FRONTEND) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines pour le développement local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour le logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)")
    return response

# Inclusion des routes API (Backend)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# --- SERVIR LES FICHIERS STATIQUES (FRONTEND) ---
# Le dossier "static" doit être dans le dossier "app"
static_path = os.path.join(os.path.dirname(__file__), "static")

# On vérifie si le dossier static existe avant de le monter
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Route principale qui sert l'interface index.html
@app.get("/")
async def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(
        status_code=404,
        content={"message": "Erreur : Fichier index.html non trouvé dans app/static/"}
    )

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée : {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue."}
    )

if __name__ == "__main__":
    import uvicorn
    # Lancement du serveur sur le port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
