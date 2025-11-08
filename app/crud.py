# app/crud.py
from typing import Dict, List, Optional
from . import schemas, auth

# --- BASE DE DATOS SIMULADA EN MEMORIA ---
# En una aplicación real, esto sería una conexión a una base de datos como PostgreSQL,
# y estas funciones ejecutarían queries SQL con SQLAlchemy.
fake_db: Dict = {
    "users": {},
    "patients": {}
}
next_user_id = 1
next_patient_id = 1

# --- FUNCIONES CRUD PARA USUARIOS ---
def get_user_by_email(email: str) -> Optional[schemas.UserInDB]:
    for user in fake_db["users"].values():
        if user["email"] == email:
            return schemas.UserInDB(**user)
    return None

def get_user_by_id(user_id: int) -> Optional[schemas.UserInDB]:
    user = fake_db["users"].get(user_id)
    if user:
        return schemas.UserInDB(**user)
    return None

def get_users(skip: int = 0, limit: int = 100) -> List[schemas.UserInDB]:
    # En una DB real, esto sería: query(User).offset(skip).limit(limit).all()
    return list(fake_db["users"].values())[skip:limit]

def create_user(user: schemas.UserCreate, role: schemas.Role = schemas.Role.physician) -> schemas.UserInDB:
    global next_user_id
    hashed_password = auth.get_password_hash(user.password)
    db_user = schemas.UserInDB(
        id=next_user_id,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
        role=role
    )
    fake_db["users"][next_user_id] = db_user.dict()
    next_user_id += 1
    return db_user

def update_user_status(user_id: int, is_active: bool) -> Optional[schemas.UserInDB]:
    db_user = get_user_by_id(user_id)
    if db_user:
        db_user.is_active = is_active
        fake_db["users"][user_id] = db_user.dict()
        return db_user
    return None

# --- FUNCIONES CRUD PARA PACIENTES ---
def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    return fake_db["patients"].get(patient_id)

def get_patients(skip: int = 0, limit: int = 100) -> List[Dict]:
    return list(fake_db["patients"].values())[skip:limit]

def create_patient(patient: schemas.PatientCreate) -> Dict:
    global next_patient_id
    db_patient = patient.dict()
    db_patient["id"] = next_patient_id
    db_patient["prediction_profile"] = None
    db_patient["prediction_description"] = None
    fake_db["patients"][next_patient_id] = db_patient
    next_patient_id += 1
    return db_patient

def update_patient(patient_id: int, patient_update: schemas.PatientUpdate) -> Optional[Dict]:
    db_patient = get_patient_by_id(patient_id)
    if not db_patient:
        return None
    
    update_data = patient_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            db_patient[key] = value
    
    fake_db["patients"][patient_id] = db_patient
    return db_patient

def delete_patient(patient_id: int) -> Optional[Dict]:
    if patient_id in fake_db["patients"]:
        return fake_db["patients"].pop(patient_id)
    return None

def update_patient_prediction(patient_id: int, profile: int, description: str) -> Optional[Dict]:
    db_patient = get_patient_by_id(patient_id)
    if db_patient:
        db_patient["prediction_profile"] = profile
        db_patient["prediction_description"] = description
        fake_db["patients"][patient_id] = db_patient
        return db_patient
    return None