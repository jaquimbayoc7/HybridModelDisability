# app/routers/patients.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
import joblib
import os

from .. import schemas, crud, dependencies, models

router = APIRouter()

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError(f"El archivo del modelo no se encontró en la ruta: {MODEL_PATH}.")

# ... (Los endpoints GET, POST, PUT, DELETE se quedan exactamente igual) ...
@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_active_medico)):
    return crud.create_user_patient(db=db, patient=patient, user_id=current_user.id)
@router.get("/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_active_medico)):
    return crud.get_patients_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Obtiene los detalles de un paciente específico.
    Solo el médico propietario puede ver su paciente.
    """
    # --- LÍNEA CORREGIDA ---
    # Cambiamos get_patient_by_id por la función correcta: get_patient
    db_patient = crud.get_patient(db, patient_id=patient_id)
    
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Verificación de propiedad
    if db_patient.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operación no permitida. No eres el propietario de este paciente.")
    
    return db_patient
@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient_details(
    patient_id: int,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Actualiza los detalles de un paciente específico.
    Solo el médico propietario puede actualizar su paciente.
    """
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Verificación de propiedad
    if db_patient.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operación no permitida. No eres el propietario de este paciente.")

    # --- LÍNEA CORREGIDA ---
    # Se pasa el objeto `db_patient` completo, no el `patient_id`.
    return crud.update_patient(db=db, db_patient=db_patient, patient_update=patient_update)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    """
    Elimina un paciente específico.
    Solo el médico propietario puede eliminar su paciente.
    """
    # --- LÍNEA CORREGIDA ---
    # Cambiamos get_patient_by_id por la función correcta: get_patient
    db_patient = crud.get_patient(db, patient_id=patient_id)
    
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Verificación de propiedad
    if db_patient.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operación no permitida. No eres el propietario de este paciente.")

    # Si todo está bien, procedemos a eliminar
    db.delete(db_patient)
    db.commit()
    
    # Devolvemos una respuesta sin contenido, como indica el código de estado 204
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{patient_id}/predict", response_model=schemas.PredictionOutput)
def predict_patient_profile(
    patient_id: int, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_medico)
):
    db_patient = read_patient(patient_id, db, current_user)
    prediction_data = schemas.PredictionInput.model_validate(db_patient)
    
    # Convertimos los datos a un DataFrame. Los nombres de las columnas
    # ('edad', 'genero', etc.) ya coinciden con lo que el nuevo modelo espera.
    input_df = pd.DataFrame([prediction_data.model_dump()])
    
    # ======================================================================
    # ¡YA NO SE NECESITA EL DICCIONARIO DE MAPEO!
    # El nuevo modelo entiende directamente las columnas del DataFrame.
    # ======================================================================

    try:
        # Pasamos el DataFrame directamente al modelo.
        prediction = model.predict(input_df)
        profile = int(prediction[0]) # La predicción ahora es un array simple
        
        # Creamos una descripción de ejemplo basada en el perfil
        descriptions = {
            0: "Perfil de Barreras Bajas",
            1: "Perfil de Barreras Moderadas",
            2: "Perfil de Barreras Altas"
        }
        description = descriptions.get(profile, "Perfil no determinado")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la ejecución del modelo: {e}")

    crud.update_patient_prediction(db, patient_id=patient_id, profile=profile, description=description)
    return {"profile": profile, "description": description}