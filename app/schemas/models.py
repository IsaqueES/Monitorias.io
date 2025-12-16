from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SubjectCreate(BaseModel):
    name: str
    image_url: str

class MonitoringCreate(BaseModel):
    subject_id: str
    monitor_name: str
    professor_name: str
    room_or_link: str
    schedule_day: str
    schedule_time: str