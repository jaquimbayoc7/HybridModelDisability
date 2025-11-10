# app/schemas.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import date
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    medico = "médico"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role: Role

class User(UserBase):
    id: int
    is_active: bool
    role: Role
    model_config = ConfigDict(from_attributes=True)

class UserStatusUpdate(BaseModel):
    is_active: bool

class PatientBase(BaseModel):
    nombre_apellidos: str
    fecha_nacimiento: date
    edad: int = Field(..., gt=0)
    genero: str
    orientacion_sexual: str
    causa_deficiencia: str
    cat_fisica: str
    cat_psicosocial: str
    nivel_d1: int = Field(..., ge=0, le=100)
    nivel_d2: int = Field(..., ge=0, le=100)
    nivel_d3: int = Field(..., ge=0, le=100)
    nivel_d4: int = Field(..., ge=0, le=100)
    nivel_d5: int = Field(..., ge=0, le=100)
    nivel_d6: int = Field(..., ge=0, le=100)
    nivel_global: int = Field(..., ge=0, le=100)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    owner_id: int
    prediction_profile: Optional[int] = None
    prediction_description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PredictionInput(BaseModel):
    edad: int
    genero: str
    orientacion_sexual: str
    causa_deficiencia: str
    cat_fisica: str
    cat_psicosocial: str
    nivel_d1: int
    nivel_d2: int
    nivel_d3: int
    nivel_d4: int
    nivel_d5: int
    nivel_d6: int
    nivel_global: int
    model_config = ConfigDict(from_attributes=True)

class PredictionOutput(BaseModel):
    profile: int
    description: str