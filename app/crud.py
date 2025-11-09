# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas, auth

# --- CRUD de Usuarios ---

def get_user_by_email(db: Session, email: str):
    """
    Busca un usuario por su dirección de correo electrónico.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """
    Busca un usuario por su ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de todos los usuarios.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, role: schemas.Role = schemas.Role.physician):
    """
    Crea un nuevo usuario en la base de datos.
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=role.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_status(db: Session, user_id: int, is_active: bool):
    """
    Actualiza el estado (activo/inactivo) de un usuario.
    """
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)
    return db_user

# --- CRUD de Pacientes ---

def get_patient_by_id(db: Session, patient_id: int):
    """
    Busca un paciente por su ID.
    """
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de todos los pacientes.
    """
    return db.query(models.Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    """
    Crea un nuevo paciente en la base de datos.
    """
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientUpdate):
    """
    Actualiza los datos de un paciente existente.
    """
    db_patient = get_patient_by_id(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
        
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    """
    Elimina un paciente de la base de datos.
    """
    db_patient = get_patient_by_id(db, patient_id)
    if db_patient:
        db.delete(db_patient)
        db.commit()
    return db_patient

def update_patient_prediction(db: Session, patient_id: int, profile: int, description: str):
    """
    Guarda el resultado de la predicción en el registro del paciente.
    """
    db_patient = get_patient_by_id(db, patient_id)
    if db_patient:
        db_patient.prediction_profile = profile
        db_patient.prediction_description = description
        db.commit()
        db.refresh(db_patient)
    return db_patient