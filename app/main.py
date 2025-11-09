# app/main.py

from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .routers import users, patients, admin
from . import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Perfilamiento de Discapacidad v3 - Final",
    description="API para la gestión de pacientes y predicción de perfiles de discapacidad.",
    version="3.0.0",
)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_email(db, email="admin@salud.co")
        if not admin_user:
            # <--- CORRECCIÓN CLAVE: Se crea el objeto UserCreate con el rol incluido
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

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(patients.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Perfilamiento de Discapacidad v3"}