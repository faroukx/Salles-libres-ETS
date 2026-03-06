from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base_class import Base
from app.services.room_service import room_service
from loguru import logger
import time
import os

# Création automatique des tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- AUTO-SYNCHRONISATION AU DÉMARRAGE ---
@app.on_event("startup")
async def startup_event():
    """
    S'exécute au démarrage du serveur. 
    Vérifie si la base de données est vide et lance une synchro auto si nécessaire.
    """
    db = SessionLocal()
    try:
        rooms = room_service.get_all_rooms(db)
        if not rooms:
            logger.info("🚀 Base de données vide au démarrage. Lancement de l'auto-synchronisation ÉTS...")
            # On définit le dossier d'upload par défaut
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Lancement de la synchro
            result = room_service.sync_from_ets_website(db, upload_dir)
            logger.info(f"✅ Auto-synchro terminée : {result.get('message')}")
        else:
            logger.info(f"ℹ️ Base de données déjà peuplée ({len(rooms)} salles). Pas de synchro nécessaire.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'auto-synchro au démarrage : {str(e)}")
    finally:
        db.close()

# --- CONFIGURATION CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
else:
    logger.error(f"Dossier static non trouvé à : {static_path}")

# Route principale qui sert l'interface publique
@app.get("/")
async def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(
        status_code=404,
        content={"message": "Erreur : Fichier index.html non trouvé"}
    )

# Route Admin
@app.get("/admin")
async def read_admin():
    admin_file = os.path.join(static_path, "admin.html")
    if os.path.exists(admin_file):
        return FileResponse(admin_file)
    return JSONResponse(
        status_code=404,
        content={"message": "Erreur : Fichier admin.html non trouvé"}
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
