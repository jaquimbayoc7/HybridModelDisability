# app/routers/patients.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
import joblib
import os

from .. import schemas, crud, dependencies, models

# ==================================================================
# CORRECCIÓN PRINCIPAL: Se eliminan 'prefix' y 'tags' de aquí.
# Ahora se gestionan únicamente en main.py, solucionando el error 404.
# ==================================================================
router = APIRouter()

# Cargar el modelo de machine learning
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError(f"El archivo del modelo no se encontró en la ruta: {MODEL_PATH}. Asegúrate de ejecutar train_model.py")

@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: schemas.PatientCreate, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Crea un nuevo registro de paciente. Solo los médicos pueden hacerlo.
    El paciente queda asignado al médico que realiza la petición.
    """
    return crud.create_user_patient(db=db, patient=patient, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Obtiene una lista de los pacientes CREADOS POR EL MÉDICO ACTUAL.
    """
    patients = crud.get_patients_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Obtiene los detalles de un paciente específico, solo si pertenece al médico actual.
    """
    # CORRECCIÓN: Se usa la función correcta de crud.py
    db_patient = crud.get_patient_by_id(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
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
    db_patient = read_patient(patient_id, db, current_user)
    # CORRECCIÓN: Se pasa el objeto db_patient directamente a la función de actualización
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
    read_patient(patient_id, db, current_user)
    crud.delete_patient(db=db, patient_id=patient_id)
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
    db_patient = read_patient(patient_id, db, current_user)

    # Convierte el objeto de la base de datos a un esquema Pydantic y luego a un DataFrame
    prediction_data = schemas.PredictionInput.model_validate(db_patient)
    input_df = pd.DataFrame([prediction_data.model_dump()])
    
    # --- SOLUCIÓN AL ERROR DE COLUMNAS ---
    # Mapeo de los nombres de columna de la API (snake_case) a los que el modelo espera (PascalCase)
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
    
    # Renombra las columnas del DataFrame
    input_df_renamed = input_df.rename(columns=column_mapping)

    try:
        # Ejecuta la predicción con el DataFrame corregido
        prediction = model.predict(input_df_renamed)
        profile = int(prediction[0, 0])
        description = str(prediction[0, 1])
    except Exception as e:
        # Captura cualquier error inesperado durante la predicción
        raise HTTPException(status_code=500, detail=f"Error durante la ejecución del modelo: {e}")

    # Guarda el resultado de la predicción en la base de datos
    crud.update_patient_prediction(db, patient_id=patient_id, profile=profile, description=description)

    # Devuelve el resultado
    return {"profile": profile, "description": description}