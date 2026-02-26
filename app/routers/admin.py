# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, dependencies, models

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/users", response_model=List[schemas.User])
def read_users(
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
