# app/routers/patients.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
import joblib
import os

from .. import schemas, crud, dependencies, models

# El router se define sin prefijo, ya que se gestiona en main.py
router = APIRouter()

# Carga del modelo de machine learning de forma segura
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError(f"El archivo del modelo no se encontró en la ruta: {MODEL_PATH}.")

@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: schemas.PatientCreate, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    return crud.create_user_patient(db=db, patient=patient, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    patients = crud.get_patients_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    if db_patient.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para acceder a este paciente")
    return db_patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient_details(
    patient_id: int,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    db_patient = read_patient(patient_id, db, current_user)
    updated_patient = crud.update_patient(db=db, patient_id=db_patient.id, patient_update=patient_update)
    return updated_patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_record(
    patient_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    db_patient = read_patient(patient_id, db, current_user)
    crud.delete_patient(db=db, patient_id=db_patient.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{patient_id}/predict", response_model=schemas.PredictionOutput)
def predict_patient_profile(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    db_patient = read_patient(patient_id, db, current_user)
    prediction_data = schemas.PredictionInput.model_validate(db_patient)
    input_df = pd.DataFrame([prediction_data.model_dump()])
    
    # Diccionario de mapeo COMPLETO Y CORRECTO
    column_mapping = {
        'edad': 'Edad',
        'genero': 'Genero',
        'orientacion_sexual': 'Orientacion_Sexual',
        'causa_deficiencia': 'Causa_Deficiencia',
        'cat_fisica': 'Cat_Fisica',
        'cat_psicosocial': 'Cat_Psicosocial',
        'nivel_d1': 'Nivel_D1',
        'nivel_d2': 'Nivel_D2',
        'nivel_d3': 'Nivel_D3',
        'nivel_d4': 'Nivel_D4',
        'nivel_d5': 'Nivel_D5',
        'nivel_d6': 'Nivel_D6',
        'nivel_global': 'Nivel_Global'
    }
    
    input_df_renamed = input_df.rename(columns=column_mapping)

    try:
        prediction = model.predict(input_df_renamed)
        profile = int(prediction[0, 0])
        description = str(prediction[0, 1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la ejecución del modelo: {e}")

    crud.update_patient_prediction(db, patient_id=patient_id, profile=profile, description=description)
    return {"profile": profile, "description": description}