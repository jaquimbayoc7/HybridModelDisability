# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, crud, dependencies

router = APIRouter(
    prefix="/admin",
    tags=["Administración (Solo para rol Admin)"],
    dependencies=[Depends(dependencies.get_current_admin_user)]
)

@router.get("/users", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100):
    """
    Lista todos los usuarios del sistema (médicos y administradores).
    Requiere rol de 'admin'.
    """
    users = crud.get_users(skip=skip, limit=limit)
    return users

@router.patch("/users/{user_id}/toggle-active", response_model=schemas.User)
def toggle_user_active(user_id: int):
    """
    Activa o desactiva un usuario (médico o admin).
    Requiere rol de 'admin'.
    """
    db_user = crud.get_user_by_id(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Opcional: Prevenir que un admin se desactive a sí mismo
    # current_admin = Depends(dependencies.get_current_admin_user)
    # if db_user.id == current_admin.id:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un administrador no puede desactivarse a sí mismo")

    updated_user = crud.update_user_status(user_id=user_id, is_active=not db_user.is_active)
    return updated_user