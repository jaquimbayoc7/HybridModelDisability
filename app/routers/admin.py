# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, dependencies
from ..database import get_db

router = APIRouter(
    dependencies=[Depends(dependencies.is_admin)]
)

@router.get("/users", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista de todos los usuarios. Solo para administradores.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.patch("/users/{user_id}/status", response_model=schemas.User)
def toggle_user_activation(user_id: int, status_update: schemas.UserStatusUpdate, db: Session = Depends(get_db)):
    """
    Activa o desactiva un usuario. Solo para administradores.
    """
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    updated_user = crud.update_user_status(db=db, user_id=user_id, is_active=status_update.is_active)
    return updated_user