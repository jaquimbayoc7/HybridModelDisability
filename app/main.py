# app/main.py

from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .routers import users, patients, admin
from . import crud, schemas
from fastapi.middleware.cors import CORSMiddleware

# Esta línea crea las tablas si no existen.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Perfilamiento de Discapacidad v3.1",
    description="API para la gestión de pacientes y predicción de perfiles de discapacidad. Desarrollado por:\n Ing. Julián Andres Quimbayo Castro - Ing. Jose Miguel Llanos Mosquera - Ing. Cindy Vargas Duque y Est. Willians Aguilar Rodriguez",
    version="1.0",
)


# Agregar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "https://e1bb997f-a232-4850-a558-28c9f9aba95b.lovableproject.com",
        "https://*.lovableproject.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"], 
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Crea el usuario administrador por defecto al iniciar la aplicación si no existe."""
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_email(db, email="administrador@salud.co")
        if not admin_user:
            admin_in = schemas.UserCreate(
                email="administrador@salud.co",
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