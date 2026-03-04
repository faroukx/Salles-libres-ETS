import os
import sys
from pathlib import Path

# Ajouter le dossier racine au chemin pour importer les modules
sys.path.append(str(Path(__file__).parent.parent))

from scripts.fetch_schedules import fetch_all_schedules
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
from app.services.pdf_parser import pdf_parser_service
from app.services.room_service import room_service
from loguru import logger

# Dossier pour les PDFs
UPLOAD_DIR = "data/uploads"

def sync_session():
    print("🔄 Démarrage de la synchronisation complète de la session...")
    
    # 1. Créer les tables si elles n'existent pas (au cas où la base a été supprimée)
    print("📂 Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Télécharger les nouveaux horaires depuis le site de l'ÉTS
    print("🌐 Téléchargement des horaires depuis le site de l'ÉTS...")
    downloaded_files = fetch_all_schedules()
    
    if not downloaded_files:
        print("⚠️ Aucun horaire n'a été téléchargé. Fin de la synchronisation.")
        return

    # 3. Analyser et importer chaque PDF téléchargé
    print(f"📄 Analyse de {len(downloaded_files)} fichiers PDF...")
    db = SessionLocal()
    try:
        total_entries = 0
        for file_path in downloaded_files:
            filename = os.path.basename(file_path)
            semester = filename.replace('.pdf', '')
            print(f"👉 Traitement de : {filename}...")
            
            extracted_data = pdf_parser_service.parse_pdf(file_path)
            
            for entry in extracted_data:
                room_name = pdf_parser_service.normalize_room_name(entry["room_name"])
                room = room_service.get_room_by_name(db, room_name)
                if not room:
                    room = room_service.create_room(db, room_name)
                
                room_service.add_schedule(
                    db, 
                    room_id=room.id,
                    day_of_week=entry["day_of_week"],
                    start_time=entry["start_time"],
                    end_time=entry["end_time"],
                    course_code=entry["course_code"],
                    semester=semester
                )
                total_entries += 1
        
        print(f"\n✅ Synchronisation terminée ! {total_entries} entrées d'horaire ont été importées.")
        
    except Exception as e:
        print(f"❌ Une erreur est survenue lors de l'importation : {e}")
        logger.error(f"Erreur sync_session: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_session()
