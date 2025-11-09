# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, Date, Float
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    nombre_apellidos = Column(String, index=True)
    fecha_nacimiento = Column(Date)
    edad = Column(Integer)
    genero = Column(String)
    orientacion_sexual = Column(String)
    causa_deficiencia = Column(String)
    cat_fisica = Column(String)
    cat_psicosocial = Column(String)
    nivel_d1 = Column(Integer)
    nivel_d2 = Column(Integer)
    nivel_d3 = Column(Integer)
    nivel_d4 = Column(Integer)
    nivel_d5 = Column(Integer)
    nivel_d6 = Column(Integer)
    nivel_global = Column(Integer)
    prediction_profile = Column(Integer, nullable=True)
    prediction_description = Column(String, nullable=True)