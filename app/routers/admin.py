# app/routers/admin.py

# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List
# from sqlalchemy.orm import Session

# # Se importa 'models' para consistencia y 'dependencies' completo
# from .. import schemas, crud, dependencies, models

# # CORRECCIÓN #1 (La Principal): Se cambia 'is_admin' por el nuevo nombre 'get_current_active_admin'
# # MEJORA: Se añaden 'prefix' y 'tags' para una mejor organización en la documentación de Swagger
# router = APIRouter(
#     prefix="/admin",
#     tags=["Admin"],
#     dependencies=[Depends(dependencies.get_current_active_admin)]
# )

# @router.get("/users", response_model=List[schemas.User])
# def read_users(
#     skip: int = 0, 
#     limit: int = 100, 
#     # MEJORA: Se usa 'dependencies.get_db' para mantener consistencia con los otros archivos
#     db: Session = Depends(dependencies.get_db)
# ):
#     """
#     Obtiene una lista de todos los usuarios. Solo para administradores.
#     """
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users

# # MEJORA: Se re-introduce la función para que el admin pueda crear usuarios (médicos)
# @router.post("/users/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
# def create_user_by_admin(
#     user: schemas.UserCreate, 
#     db: Session = Depends(dependencies.get_db)
# ):
#     """
#     Crea un nuevo usuario (médico o admin). Solo para administradores.
#     """
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
#     return crud.create_user(db=db, user=user)


# @router.patch("/users/{user_id}/status", response_model=schemas.User)
# def toggle_user_activation(
#     user_id: int, 
#     status_update: schemas.UserStatusUpdate, 
#     db: Session = Depends(dependencies.get_db)
# ):
#     """
#     Activa o desactiva un usuario. Solo para administradores.
#     """
#     # CORRECCIÓN #2: Se usa 'crud.get_user' que es la función correcta en nuestro crud.py
#     db_user = crud.get_user(db, user_id=user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
#     # CORRECCIÓN #2: Se usa 'crud.update_user_activity' que es la función correcta
#     updated_user = crud.update_user_activity(db=db, user_id=user_id, is_active=status_update.is_active)
#     return updated_user

# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, dependencies, models

# Router SIN dependencias globales
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# Manejador OPTIONS para CORS preflight (sin autenticación)
@router.options("/users")
@router.options("/users/register")
@router.options("/users/{user_id}/status")
async def options_handler():
    return {}

# Ahora las rutas con autenticación
@router.get("/users", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_admin)
):
    """Obtiene una lista de todos los usuarios. Solo para administradores."""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/users/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    user: schemas.UserCreate, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_admin)
):
    """Crea un nuevo usuario (médico o admin). Solo para administradores."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    return crud.create_user(db=db, user=user)

@router.patch("/users/{user_id}/status", response_model=schemas.User)
def toggle_user_activation(
    user_id: int, 
    status_update: schemas.UserStatusUpdate, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_admin)
):
    """Activa o desactiva un usuario. Solo para administradores."""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    updated_user = crud.update_user_activity(db=db, user_id=user_id, is_active=status_update.is_active)
    return updated_user
