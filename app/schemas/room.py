from pydantic import BaseModel, Field
from datetime import time, date
from typing import List, Optional

# --- ROOM SCHEMAS ---
class RoomBase(BaseModel):
    name: str
    building: Optional[str] = None
    floor: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    class Config:
        from_attributes = True

# --- SCHEDULE SCHEMAS ---
class ScheduleBase(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time
    course_code: Optional[str] = None
    semester: str

class ScheduleCreate(ScheduleBase):
    room_id: int

class ScheduleResponse(ScheduleBase):
    id: int
    room: RoomResponse
    class Config:
        from_attributes = True

# --- AVAILABILITY SCHEMAS ---
class AvailableRoomResponse(BaseModel):
    room_name: str
    is_available: bool
    free_until: Optional[time] = None
    remaining_duration_minutes: Optional[int] = None
    next_course_at: Optional[time] = None
    current_course_code: Optional[str] = None  # NOUVEAU: Code du cours en cours
    next_course_code: Optional[str] = None     # NOUVEAU: Code du prochain cours

class AvailabilityQuery(BaseModel):
    date: date
    time: time
