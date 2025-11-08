# app/main.py
from fastapi import FastAPI
from .routers import users, patients, admin
from . import crud, schemas

app = FastAPI(
    title="API de Perfilado de Pacientes v2",
    description="API completa para la gestión de pacientes, médicos y predicciones de perfil, con roles y autenticación.",
    version="2.0.0"
)

@app.on_event("startup")
def on_startup():
    """
    Se ejecuta al iniciar la aplicación.
    Crea el usuario administrador por defecto si no existe.
    """
    admin_user = crud.get_user_by_email("admin@salud.co")
    if not admin_user:
        admin_in = schemas.UserCreate(
            email="admin@salud.co",
            password="adminpassword", # En producción, usar una variable de entorno
            full_name="Administrador del Sistema"
        )
        crud.create_user(user=admin_in, role=schemas.Role.admin)
        print("--- USUARIO ADMIN CREADO ---")
        print("Email: admin@salud.co")
        print("Password: adminpassword")
        print("-----------------------------")

# Incluir los routers de las diferentes secciones de la API
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(admin.router)

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint de bienvenida a la API."""
    return {"message": "Bienvenido a la API de Perfilado de Pacientes v2. Visita /docs para la documentación interactiva."}