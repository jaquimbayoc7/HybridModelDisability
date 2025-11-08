# app/routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, crud, dependencies
import pandas as pd
import joblib
import os

router = APIRouter(
    prefix="/patients",
    tags=["Pacientes (CRUD y Predicción)"],
    dependencies=[Depends(dependencies.get_current_active_user)]
)

# Cargar el modelo al iniciar el router
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"ADVERTENCIA: No se encontró el modelo en {MODEL_PATH}. El endpoint de predicción fallará.")

@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(patient: schemas.PatientCreate):
    """Crea un nuevo registro de paciente."""
    return crud.create_patient(patient=patient)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100):
    """Obtiene una lista de todos los pacientes con sus predicciones (si existen)."""
    patients = crud.get_patients(skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int):
    """Obtiene los datos de un paciente específico por su ID."""
    db_patient = crud.get_patient_by_id(patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return db_patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient: schemas.PatientUpdate):
    """Actualiza los datos de un paciente. Permite actualizaciones parciales."""
    db_patient = crud.update_patient(patient_id=patient_id, patient_update=patient)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return db_patient

@router.delete("/{patient_id}", response_model=schemas.Patient)
def delete_patient(patient_id: int):
    """Elimina un paciente de la base de datos."""
    db_patient = crud.delete_patient(patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return db_patient

@router.post("/{patient_id}/predict", response_model=schemas.PredictionResponse)
def predict_patient_profile(patient_id: int):
    """Activa el modelo para generar y guardar el perfil de un paciente."""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de predicción no disponible. Modelo no cargado."
        )
    
    patient_data = crud.get_patient_by_id(patient_id=patient_id)
    if not patient_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")

    # Preparar datos para el modelo
    input_data = pd.DataFrame([patient_data])
    
    # Realizar predicción
    prediction = model.predict(input_data)
    predicted_profile = int(prediction[0])

    profile_mapping = {0: "Alta percepción", 1: "Moderada percepción", 2: "Baja Percepción"}
    description = profile_mapping.get(predicted_profile, "Perfil desconocido")

    # Guardar la predicción en el registro del paciente
    crud.update_patient_prediction(patient_id, predicted_profile, description)

    return {
        "patient_id": patient_id,
        "prediction_profile": predicted_profile,
        "prediction_description": description
    }