# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Lee la URL de la base de datos desde una variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

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