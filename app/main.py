# app/main.py

from fastapi import FastAPI
from .routers import users, patients, admin
from . import crud, schemas, models
from .database import SessionLocal, engine

# Esta línea crea todas las tablas definidas en models.py en la base de datos
# si no existen. Es seguro ejecutarla cada vez que la aplicación inicia.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Perfilado de Pacientes v2 - PostgreSQL",
    description="API para la gestión de pacientes y predicción de perfiles de discapacidad, ahora con base de datos PostgreSQL.",
    version="2.0.0",
)

@app.on_event("startup")
def on_startup():
    """
    Crea el usuario administrador por defecto al iniciar la aplicación si no existe.
    Usa una sesión de base de datos para realizar la operación.
    """
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_email(db, email="admin@salud.co")
        if not admin_user:
            admin_in = schemas.UserCreate(
                email="admin@salud.co",
                password="adminpassword",
                full_name="Administrador del Sistema"
            )
            crud.create_user(db=db, user=admin_in, role=schemas.Role.admin)
            print("Usuario administrador por defecto creado.")
    finally:
        db.close()

# Incluir los routers de las diferentes secciones de la API
app.include_router(users.router, prefix="/users", tags=["Users & Authentication"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Perfilado de Pacientes v2"}