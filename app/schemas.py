# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum

# --- ENUMS ---
class Role(str, Enum):
    admin = "admin"
    physician = "physician"

class GeneroEnum(str, Enum):
    femenino = "Femenino"
    masculino = "Masculino"
    no_responde = "No responde"

class OrientacionSexualEnum(str, Enum):
    heterosexual = "Heterosexual"
    no_responde = "No responde"

class CausaDeficienciaEnum(str, Enum):
    alteracion_genetica = "Alteración genética o hereditaria"
    enfermedad_general = "Enfermedad general"
    accidente_transito = "Accidente de tránsito"
    parto_complicaciones = "Complicaciones durante el parto"
    desarrollo_embrionario = "Alteraciones del desarrollo embrionario"
    accidente_hogar = "Accidente en el hogar"
    accidente_trabajo = "Accidente de trabajo"
    violencia_comun = "Violencia por delincuencia común"

class CatFisicaEnum(str, Enum):
    si = "SI"
    no = "NO"

class CatPsicosocialEnum(str, Enum):
    si = "SI"
    no = "NO"

# --- TOKEN ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- USER ---
class UserBase(BaseModel):
    email: EmailStr = Field(..., example="medico@salud.co")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="password123")
    full_name: str = Field(..., example="Dr. Juan Pérez")

class UserInDB(UserBase):
    id: int
    full_name: str
    hashed_password: str
    is_active: bool
    role: Role

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    role: Role
    class Config:
        orm_mode = True

# --- PATIENT ---
class PatientBase(BaseModel):
    nombre_apellidos: str = Field(..., example="Ana García López")
    fecha_nacimiento: date = Field(..., example="1995-05-20")
    edad: int = Field(..., ge=0, example=29)
    genero: GeneroEnum
    orientacion_sexual: OrientacionSexualEnum
    causa_deficiencia: CausaDeficienciaEnum
    cat_fisica: CatFisicaEnum
    cat_psicosocial: CatPsicosocialEnum
    nivel_d1: int = Field(..., ge=0, le=100)
    nivel_d2: int = Field(..., ge=0, le=100)
    nivel_d3: int = Field(..., ge=0, le=100)
    nivel_d4: int = Field(..., ge=0, le=100)
    nivel_d5: int = Field(..., ge=0, le=100)
    nivel_d6: int = Field(..., ge=0, le=100)
    nivel_global: int = Field(..., ge=0, le=100)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    nombre_apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    edad: Optional[int] = None
    genero: Optional[GeneroEnum] = None
    orientacion_sexual: Optional[OrientacionSexualEnum] = None
    causa_deficiencia: Optional[CausaDeficienciaEnum] = None
    cat_fisica: Optional[CatFisicaEnum] = None
    cat_psicosocial: Optional[CatPsicosocialEnum] = None
    nivel_d1: Optional[int] = None
    nivel_d2: Optional[int] = None
    nivel_d3: Optional[int] = None
    nivel_d4: Optional[int] = None
    nivel_d5: Optional[int] = None
    nivel_d6: Optional[int] = None
    nivel_global: Optional[int] = None

class Patient(PatientBase):
    id: int
    prediction_profile: Optional[int] = None
    prediction_description: Optional[str] = None
    class Config:
        orm_mode = True

class PredictionResponse(BaseModel):
    patient_id: int
    prediction_profile: int
    prediction_description: str