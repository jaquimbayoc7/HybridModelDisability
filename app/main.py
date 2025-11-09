# app/main.py

from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .routers import users, patients, admin
from . import crud, schemas

# Esta línea crea las tablas si no existen.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Perfilamiento de Discapacidad v3.1",
    description="API para la gestión de pacientes y predicción de perfiles de discapacidad.",
    version="3.1.0",
)

@app.on_event("startup")
def on_startup():
    """Crea el usuario administrador por defecto al iniciar la aplicación si no existe."""
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_email(db, email="admin@salud.co")
        if not admin_user:
            admin_in = schemas.UserCreate(
                email="admin@salud.co",
                password="adminpassword",
                full_name="Administrador del Sistema",
                role=schemas.Role.admin
            )
            crud.create_user(db=db, user=admin_in)
            print("Usuario administrador por defecto creado.")
    finally:
        db.close()

# ======================================================================
# CORRECCIÓN CLAVE: Asegurarse de que TODOS los routers están incluidos
# correctamente con sus prefijos. Esta sección es la que resuelve el 404.
# ======================================================================
app.include_router(users.router, prefix="/users", tags=["Users & Authentication"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raíz de bienvenida."""
    return {"message": "Bienvenido a la API de Perfilamiento de Discapacidad v3.1"}