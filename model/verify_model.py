# verify_model.py

import pandas as pd
import joblib
import os

print("--- Iniciando Script de Verificación del Modelo Unificado ---")

# --- 1. Cargar el modelo recién generado ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model_pipeline.joblib')
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Modelo cargado exitosamente.")
except FileNotFoundError:
    print("❌ ERROR: No se encontró el modelo. Ejecuta 'python train_model.py' primero.")
    exit()

# --- 2. Crear datos de prueba que simulan la entrada de la API ---
# Los nombres de las columnas ('edad', 'genero', etc.) son ahora la única fuente de verdad.
test_data = {
    'edad': 42,
    'genero': 'Masculino',
    'orientacion_sexual': 'Heterosexual',
    'causa_deficiencia': 'Accidente de tránsito',
    'cat_fisica': 'NO',
    'cat_psicosocial': 'SI',
    'nivel_d1': 25,
    'nivel_d2': 50,
    'nivel_d3': 75,
    'nivel_d4': 100,
    'nivel_d5': 50,
    'nivel_d6': 25,
    'nivel_global': 55
}
input_df = pd.DataFrame([test_data])
print("\nDataFrame de prueba creado (formato directo de la API):")
print(input_df)

# --- 3. Intentar la predicción (SIN RENOMBRAR COLUMNAS) ---
try:
    print("\nIntentando realizar la predicción directa...")
    prediction = model.predict(input_df)
    print(f"\n✅ ¡ÉXITO TOTAL! La predicción funcionó sin errores.")
    print(f"   Resultado de la predicción: {prediction}")

    # --- 4. Verificación Interna Definitiva ---
    print("\n--- Verificación Interna del Modelo ---")
    # Obtenemos las características que el preprocesador del modelo aprendió a usar.
    feature_names = model.named_steps['preprocessor'].get_feature_names_out()
    print("El modelo fue entrenado y espera las siguientes características (o variaciones):")
    
    # Buscamos pruebas de que aprendió de las columnas correctas
    test_cols = ['num__edad', 'cat__genero_Masculino', 'cat__causa_deficiencia_Accidente de tránsito']
    for col in test_cols:
        if col in feature_names:
            print(f"  - Encontrado: '{col}' (¡Correcto!)")
        else:
            print(f"  - NO Encontrado: '{col}' (¡Error!)")
    print("-----------------------------------------")

except Exception as e:
    print(f"\n❌ ¡FALLO! La predicción falló con el siguiente error:")
    print(e)
    print("\nSi ves este error, significa que el modelo en 'model_pipeline.joblib' todavía no está alineado con la API.")

print("\n--- Fin del Script de Verificación ---")