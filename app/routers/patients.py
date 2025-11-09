# app/routers/patients.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
import joblib
import os

# Se importan todos los módulos necesarios del proyecto
from .. import schemas, crud, dependencies, models

# Se quita get_db porque ahora se obtiene a través de dependencies
# para mantener la consistencia

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    # La dependencia se aplica por endpoint para mayor claridad y flexibilidad
)

# Cargar el modelo de machine learning
# La ruta que tenías es correcta si la carpeta 'model' está en la raíz del proyecto
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError(f"El archivo del modelo no se encontró en la ruta: {MODEL_PATH}. Asegúrate de ejecutar train_model.py")

@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: schemas.PatientCreate, 
    db: Session = Depends(dependencies.get_db),
    # CORRECCIÓN: Se inyecta el usuario actual para saber quién es el dueño del paciente
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Crea un nuevo registro de paciente. Solo los médicos pueden hacerlo.
    El paciente queda asignado al médico que realiza la petición.
    """
    # CORRECCIÓN: Se llama a una función CRUD que asigna el owner_id
    return crud.create_user_patient(db=db, patient=patient, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(dependencies.get_db),
    # CORRECCIÓN: Se necesita saber quién es el usuario para filtrar sus pacientes
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Obtiene una lista de los pacientes CREADOS POR EL MÉDICO ACTUAL.
    """
    # CORRECCIÓN: Se llama a una función que filtra por el ID del dueño (owner_id)
    patients = crud.get_patients_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    # CORRECCIÓN: Se necesita al usuario para verificar permisos
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Obtiene los detalles de un paciente específico, solo si pertenece al médico actual.
    """
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # CORRECCIÓN DE SEGURIDAD: Verificar que el paciente pertenece al médico
    if db_patient.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para acceder a este paciente")
        
    return db_patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int, 
    patient: schemas.PatientUpdate, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Actualiza la información de un paciente, solo si pertenece al médico actual.
    """
    # Reutilizamos la función anterior para obtener y validar el paciente en un solo paso
    db_patient = read_patient(patient_id, db, current_user)
    return crud.update_patient(db=db, db_patient=db_patient, patient_update=patient)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Elimina un paciente, solo si pertenece al médico actual.
    """
    # Validamos que el paciente existe y pertenece al médico
    read_patient(patient_id, db, current_user)
    crud.delete_patient(db=db, patient_id=patient_id)
    # No se devuelve contenido en un 204
    return

@router.post("/{patient_id}/predict", response_model=schemas.PredictionOutput)
def predict_patient_profile(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Ejecuta la predicción para un paciente, solo si pertenece al médico actual.
    """
    # Reutilizamos la lógica de permisos para obtener el paciente
    db_patient = read_patient(patient_id, db, current_user)

    # CORRECCIÓN: Se usan los métodos modernos de Pydantic v2 para la conversión
    prediction_data = schemas.PredictionInput.model_validate(db_patient)
    input_df = pd.DataFrame([prediction_data.model_dump()])
    
    # Realizar la predicción
    try:
        # CORRECCIÓN: El modelo devuelve dos valores (perfil y clasificación)
        prediction = model.predict(input_df)
        profile = int(prediction[0, 0])
        description = str(prediction[0, 1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la ejecución del modelo: {e}")

    # Guardar la predicción en la base de datos
    crud.update_patient_prediction(db, patient_id=patient_id, profile=profile, description=description)

    return {"profile": profile, "description": description}