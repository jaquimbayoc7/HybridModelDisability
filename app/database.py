# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Lee la URL de la base de datos desde una variable de entorno
# IMPORTANTE: Render proporciona la URL con formato postgresql:// 
# que SQLAlchemy 2.0+ requiere convertir a postgresql+psycopg2://
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"  # Fallback para desarrollo local
)

# Conversión necesaria para Render (psycopg2)
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Crea el motor de SQLAlchemy
# Para SQLite en desarrollo, deshabilita validación de foreign keys
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Para PostgreSQL en producción
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True  # Verifica conexiones antes de usarlas
    )

# Crea una clase SessionLocal para las sesiones de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para que nuestros modelos ORM hereden de ella
Base = declarative_base()

# Dependencia para obtener la sesión de la DB en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()