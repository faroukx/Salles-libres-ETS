from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import date, time, datetime
from typing import List, Optional
import os
import shutil
from app.db.session import get_db
from app.services.room_service import room_service
from app.services.pdf_parser import pdf_parser_service
from app.schemas.room import RoomResponse, AvailableRoomResponse
from app.core.config import settings
from loguru import logger

router = APIRouter()

@router.get("/rooms", response_model=List[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    """Retourne la liste de toutes les salles enregistrées."""
    return room_service.get_all_rooms(db)

@router.get("/available-rooms", response_model=List[AvailableRoomResponse])
def get_available_rooms(
    date_str: str = Query(..., alias="date", description="Date au format YYYY-MM-DD"),
    time_str: str = Query(..., alias="time", description="Heure au format HH:MM"),
    db: Session = Depends(get_db)
):
    """Trouve les salles disponibles à une date et heure données."""
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        query_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date ou d'heure invalide. Utilisez YYYY-MM-DD et HH:MM")

    return room_service.get_available_rooms(db, query_date, query_time)

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    semester: str = Query(..., description="Semestre (ex: Hiver 2024)"),
    db: Session = Depends(get_db)
):
    """Upload un PDF d'horaire, l'analyse et remplit la base de données."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")

    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    try:
        # Sauvegarder le fichier localement
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parser le PDF
        extracted_data = pdf_parser_service.parse_pdf(file_path)
        
        count = 0
        for entry in extracted_data:
            # Gérer la salle (créer si inexistante)
            room_name = pdf_parser_service.normalize_room_name(entry["room_name"])
            room = room_service.get_room_by_name(db, room_name)
            if not room:
                room = room_service.create_room(db, room_name)
            
            # Ajouter à l'horaire
            room_service.add_schedule(
                db, 
                room_id=room.id,
                day_of_week=entry["day_of_week"],
                start_time=entry["start_time"],
                end_time=entry["end_time"],
                course_code=entry["course_code"],
                semester=semester
            )
            count += 1
            
        return {
            "status": "success",
            "message": f"{count} entrées d'horaire importées avec succès",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du PDF: {str(e)}")

@router.post("/reload-data")
def reload_data(db: Session = Depends(get_db)):
    """Scan le dossier d'uploads et recharge tous les PDFs présents en base."""
    try:
        if not os.path.exists(settings.UPLOAD_DIR):
            return {"status": "info", "message": "Le dossier d'uploads est vide ou inexistant."}
            
        files = [f for f in os.listdir(settings.UPLOAD_DIR) if f.lower().endswith('.pdf')]
        if not files:
            return {"status": "info", "message": "Aucun fichier PDF trouvé dans le dossier d'uploads."}
            
        total_count = 0
        for filename in files:
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            extracted_data = pdf_parser_service.parse_pdf(file_path)
            
            semester = filename.replace('.pdf', '')
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
                total_count += 1
                
        return {
            "status": "success", 
            "message": f"Rechargement terminé : {len(files)} fichiers traités, {total_count} entrées ajoutées."
        }
    except Exception as e:
        logger.error(f"Erreur lors du rechargement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du rechargement: {str(e)}")

@router.post("/sync-ets")
def sync_ets(db: Session = Depends(get_db)):
    """Télécharge les horaires depuis le site de l'ÉTS et les recharge automatiquement."""
    try:
        from scripts.fetch_schedules import fetch_all_schedules
        
        # 1. Télécharger les fichiers
        downloaded_files = fetch_all_schedules()
        
        if not downloaded_files:
            return {"status": "error", "message": "Aucun horaire n'a pu être téléchargé depuis le site de l'ÉTS."}
            
        # 2. Recharger les données (on réutilise la logique de reload_data)
        return reload_data(db)
        
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la synchronisation: {str(e)}")

@router.delete("/clear-data")
def clear_data(db: Session = Depends(get_db)):
    """Supprime toutes les données de la base de données."""
    room_service.clear_all_data(db)
    return {"status": "success", "message": "Toutes les données ont été supprimées"}
