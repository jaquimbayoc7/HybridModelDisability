# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .. import schemas, auth, dependencies

# El router no lleva prefijo aquí, lo cual es correcto.
router = APIRouter()

# Se elimina el endpoint de registro público (/register).
# La creación de usuarios ahora es responsabilidad exclusiva del admin
# a través del endpoint /admin/users/register.

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(dependencies.get_db)
):
    """
    Proporciona un token de acceso para un usuario autenticado.
    """
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Cuenta de usuario inactiva")
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # ======================================================================
    # CORRECCIÓN CLAVE: Se añade el 'role' del usuario al payload del token.
    # Sin esto, las rutas protegidas por rol nunca funcionarán.
    # ======================================================================
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}