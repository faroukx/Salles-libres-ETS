from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import time, date, datetime, timedelta
from typing import List, Optional, Dict, Any
import os
from app.models.room import Room, Schedule
from app.schemas.room import AvailableRoomResponse
from loguru import logger

class RoomService:
    def get_all_rooms(self, db: Session) -> List[Room]:
        return db.query(Room).all()

    def get_room_by_name(self, db: Session, name: str) -> Optional[Room]:
        return db.query(Room).filter(Room.name == name).first()

    def create_room(self, db: Session, name: str) -> Room:
        building = name.split('-')[0] if '-' in name else "Autre"
        floor = "0"
        if '-' in name:
            parts = name.split('-')
            if len(parts) > 1 and len(parts[1]) > 0:
                floor = parts[1][0]
        
        room = Room(name=name, building=building, floor=floor)
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    def add_schedule(self, db: Session, room_id: int, day_of_week: int, 
                     start_time: time, end_time: time, course_code: str, semester: str) -> Schedule:
        existing = db.query(Schedule).filter(
            Schedule.room_id == room_id,
            Schedule.day_of_week == day_of_week,
            Schedule.start_time == start_time,
            Schedule.end_time == end_time,
            Schedule.course_code == course_code,
            Schedule.semester == semester
        ).first()
        
        if existing:
            return existing

        schedule = Schedule(
            room_id=room_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            course_code=course_code,
            semester=semester
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    def get_available_rooms(self, db: Session, query_date: date, query_time: time) -> List[AvailableRoomResponse]:
        day_of_week = query_date.weekday()
        all_rooms = db.query(Room).all()
        results = []

        for room in all_rooms:
            current_course = db.query(Schedule).filter(
                Schedule.room_id == room.id,
                Schedule.day_of_week == day_of_week,
                Schedule.start_time <= query_time,
                Schedule.end_time > query_time
            ).first()

            is_free = current_course is None

            next_course = db.query(Schedule).filter(
                Schedule.room_id == room.id,
                Schedule.day_of_week == day_of_week,
                Schedule.start_time > query_time
            ).order_by(Schedule.start_time).first()

            if is_free:
                free_until = next_course.start_time if next_course else time(23, 0)
                duration = self._calculate_duration_minutes(query_time, free_until)
                
                results.append(AvailableRoomResponse(
                    room_name=room.name,
                    is_available=True,
                    free_until=free_until,
                    remaining_duration_minutes=max(0, duration),
                    next_course_at=next_course.start_time if next_course else None,
                    current_course_code=None,
                    next_course_code=next_course.course_code if next_course else None
                ))
            else:
                results.append(AvailableRoomResponse(
                    room_name=room.name,
                    is_available=False,
                    free_until=current_course.end_time,
                    remaining_duration_minutes=0,
                    next_course_at=current_course.end_time,
                    current_course_code=current_course.course_code,
                    next_course_code=next_course.course_code if next_course else None
                ))

        return sorted(results, key=lambda x: (not x.is_available, -x.remaining_duration_minutes if x.remaining_duration_minutes else 0))

    def _calculate_duration_minutes(self, start: time, end: time) -> int:
        start_dt = datetime.combine(date.today(), start)
        end_dt = datetime.combine(date.today(), end)
        diff = end_dt - start_dt
        return int(diff.total_seconds() / 60)

    def clear_all_data(self, db: Session):
        db.query(Schedule).delete()
        db.query(Room).delete()
        db.commit()

    def reload_all_data(self, db: Session, upload_dir: str):
        from app.services.pdf_parser import pdf_parser_service
        
        if not os.path.exists(upload_dir):
            return {"status": "error", "message": f"Dossier {upload_dir} introuvable."}
        
        files = [f for f in os.listdir(upload_dir) if f.lower().endswith('.pdf')]
        if not files:
            return {"status": "info", "message": "Aucun fichier PDF trouvé."}
        
        total_count = 0
        for filename in files:
            file_path = os.path.join(upload_dir, filename)
            try:
                semester = filename.replace('.pdf', '')
                extracted_data = pdf_parser_service.parse_pdf(file_path)
                
                for entry in extracted_data:
                    room_name = pdf_parser_service.normalize_room_name(entry["room_name"])
                    room = self.get_room_by_name(db, room_name)
                    if not room:
                        room = self.create_room(db, room_name)
                    
                    self.add_schedule(
                        db, 
                        room_id=room.id,
                        day_of_week=entry["day_of_week"],
                        start_time=entry["start_time"],
                        end_time=entry["end_time"],
                        course_code=entry["course_code"],
                        semester=semester
                    )
                    total_count += 1
            except Exception as e:
                logger.error(f"Erreur rechargement {filename}: {str(e)}")
        
        return {"status": "success", "message": f"{len(files)} fichiers traités, {total_count} entrées ajoutées."}

    def sync_from_ets_website(self, db: Session, upload_dir: str):
        from scripts.fetch_schedules import fetch_all_schedules
        downloaded_files = fetch_all_schedules(filter_current=True)
        
        if not downloaded_files:
            return {"status": "info", "message": "Aucun horaire correspondant à la session actuelle n'a été trouvé."}
            
        return self.reload_all_data(db, upload_dir)

room_service = RoomService()
