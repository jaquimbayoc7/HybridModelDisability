# app/auth.py

from fastapi import Depends, HTTPException, status
# <--- CORRECCIÓN #1: Importar la clase que falta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os

# Imports para la función de autenticación
from . import crud, schemas

# --- Configuración de Seguridad ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORRECCIÓN CRÍTICA: Se obtiene SECRET_KEY con un valor por defecto
# En producción (Render), DEBE estar configurada como variable de entorno
# En desarrollo, se usa una clave por defecto (NO SEGURA - solo para desarrollo)
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key-change-in-production-12345678901234567890"  # ⚠️ Solo para desarrollo
)

if SECRET_KEY.startswith("dev-secret-key"):
    import warnings
    warnings.warn(
        "⚠️ Usando SECRET_KEY de desarrollo. En producción, configura la variable de entorno SECRET_KEY."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ======================================================================
# CORRECCIÓN #2: AÑADIR ESTA LÍNEA ES LA SOLUCIÓN AL ERROR 404
# Esta línea crea el esquema de seguridad y le dice a Swagger
# que la URL para obtener el token es /users/login.
# ======================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# --- Funciones de Contraseña ---

def verify_password(plain_password, hashed_password):
    """Verifica que una contraseña en texto plano coincida con su versión hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera el hash de una contraseña en texto plano."""
    return pwd_context.hash(password)

# --- Función de Autenticación de Usuario ---

def authenticate_user(db: Session, email: str, password: str):
    """
    Autentica a un usuario. Devuelve el objeto de usuario si es exitoso, si no, None.
    """
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# --- Funciones de Token JWT ---

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un nuevo token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        # CORRECCIÓN: Usar datetime.now(timezone.utc) para consistencia
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt