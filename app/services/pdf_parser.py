import pdfplumber
import re
from datetime import time
from typing import List, Dict, Any
from loguru import logger

class PDFParserService:
    def __init__(self):
        # Regex améliorée pour le format spécifique de l'ÉTS
        # Groupe 1: Code de cours (ex: ATE075)
        # Groupe 2: Jour (ex: Mer)
        # Groupe 3: Heure début (ex: 09:00)
        # Groupe 4: Heure fin (ex: 12:30)
        # Groupe 5: Local (ex: E-2025 ou D-5019, A-1222)
        self.pattern = re.compile(
            r'([A-Z]{3}\d{3})\s+.*?\s+(Lun|Mar|Mer|Jeu|Ven|Sam|Dim)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s+.*?\s+([A-Z]-\d{4}(?:,\s*[A-Z]-\d{4})*)',
            re.IGNORECASE | re.DOTALL
        )
        self.day_mapping = {
            "Lun": 0, "Mar": 1, "Mer": 2, "Jeu": 3, "Ven": 4, "Sam": 5, "Dim": 6
        }

    def parse_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        extracted_data = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Utilisation de l'extraction de table ou de texte structuré
                    text = page.extract_text(layout=True)
                    if not text:
                        continue
                    
                    # On nettoie un peu le texte pour faciliter le matching
                    lines = text.split('\n')
                    current_course = None
                    
                    for line in lines:
                        # Détection du code de cours en début de ligne
                        course_match = re.match(r'^([A-Z]{3}\d{3})', line.strip())
                        if course_match:
                            current_course = course_match.group(1)
                        
                        # Recherche des infos de plage horaire
                        # Format: Jour Heure Activité Mode Local
                        # Ex: Mer 09:00 - 12:30 Atelier P E-2025
                        schedule_match = re.search(
                            r'(Lun|Mar|Mer|Jeu|Ven|Sam|Dim)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s+.*?\s+([A-Z]-\d{4}(?:,\s*[A-Z]-\d{4})*)',
                            line
                        )
                        
                        if schedule_match and current_course:
                            day_str, start_str, end_str, rooms_str = schedule_match.groups()
                            
                            day_of_week = self.day_mapping.get(day_str.capitalize())
                            start_time = self._parse_time(start_str)
                            end_time = self._parse_time(end_str)
                            
                            # Gérer les locaux multiples (ex: D-5019, A-1222)
                            room_names = [r.strip() for r in rooms_str.split(',')]
                            
                            for room_name in room_names:
                                extracted_data.append({
                                    "course_code": current_course,
                                    "day_of_week": day_of_week,
                                    "start_time": start_time,
                                    "end_time": end_time,
                                    "room_name": room_name.upper()
                                })
            
            logger.info(f"Parsed {len(extracted_data)} schedule entries from {file_path}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")

    def _parse_time(self, time_str: str) -> time:
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)

    def normalize_room_name(self, room_name: str) -> str:
        return room_name.strip().upper()

pdf_parser_service = PDFParserService()
