# app/routers/patients.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
import joblib
import os

from .. import schemas, crud, dependencies
from ..database import get_db

router = APIRouter(
    dependencies=[Depends(dependencies.is_physician)]
)

# Cargar el modelo de machine learning
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError(f"El archivo del modelo no se encontró en la ruta: {MODEL_PATH}. Asegúrate de ejecutar train_model.py")

@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo registro de paciente.
    """
    return crud.create_patient(db=db, patient=patient)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista de todos los pacientes.
    """
    patients = crud.get_patients(db=db, skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un paciente específico por su ID.
    """
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return db_patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de un paciente existente.
    """
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return crud.update_patient(db=db, patient_id=patient_id, patient_update=patient)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Elimina un registro de paciente.
    """
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    crud.delete_patient(db=db, patient_id=patient_id)
    return {"detail": "Paciente eliminado exitosamente"}

@router.post("/{patient_id}/predict", response_model=schemas.PredictionOutput)
def predict_patient_profile(patient_id: int, db: Session = Depends(get_db)):
    """
    Ejecuta el modelo de predicción para un paciente existente y guarda el resultado.
    """
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Crear un DataFrame con los datos del paciente para el modelo
    input_data = pd.DataFrame([schemas.PredictionInput.from_orm(db_patient).dict()])
    
    # Realizar la predicción
    prediction = model.predict(input_data)
    profile = int(prediction[0])

    # Mapear el perfil a una descripción
    profile_descriptions = {
        0: "Perfil 0: Descripción del perfil de percepción.",
        1: "Perfil 1: Descripción del perfil de percepción.",
        2: "Perfil 2: Descripción del perfil de percepción."
    }
    description = profile_descriptions.get(profile, "Perfil desconocido")

    # Guardar la predicción en la base de datos
    crud.update_patient_prediction(db, patient_id=patient_id, profile=profile, description=description)

    return {"profile": profile, "description": description}