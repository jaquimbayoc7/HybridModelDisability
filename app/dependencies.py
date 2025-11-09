# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# CORRECCIÓN 1: Se importa 'models' para usar los tipos de la base de datos
from . import schemas, crud, auth, models
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# CORRECCIÓN 2: Se simplifican las funciones a síncronas (se quita 'async')
# ya que no realizan operaciones de I/O que requieran 'await'.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # CORRECCIÓN 3: El tipo de 'user' es 'models.User', que es lo que devuelve CRUD
    user: models.User = crud.get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# El tipo de 'current_user' es 'models.User' porque eso es lo que devuelve 'get_current_user'
def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

# CORRECCIÓN 4: Renombrada de 'is_admin' a 'get_current_active_admin' por consistencia
def get_current_active_admin(current_user: models.User = Depends(get_current_active_user)) -> models.User:
    # Se compara directamente con el string del rol para mayor claridad
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación no permitida. Se requiere rol de administrador."
        )
    return current_user

# CORRECCIÓN 5: Renombrada de 'is_physician' a 'get_current_active_medico'
# ESTA ES LA CORRECCIÓN PRINCIPAL QUE SOLUCIONA EL ERROR DE DESPLIEGUE
def get_current_active_medico(current_user: models.User = Depends(get_current_active_user)) -> models.User:
    # Se compara con 'médico' para alinearse con el Enum de 'schemas.py'
    if current_user.role != "médico":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación no permitida. Se requiere rol de médico."
        )
    return current_user