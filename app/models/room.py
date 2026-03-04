from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    building = Column(String)
    floor = Column(String)
    schedules = relationship("Schedule", back_populates="room", cascade="all, delete-orphan")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    day_of_week = Column(Integer)  # 0=Lundi, 6=Dimanche
    start_time = Column(Time)
    end_time = Column(Time)
    course_code = Column(String, nullable=True)
    semester = Column(String)
    
    room = relationship("Room", back_populates="schedules")

class PDFUpload(Base):
    __tablename__ = "pdf_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=func.now())
    status = Column(String)  # 'PENDING', 'PROCESSED', 'FAILED'
