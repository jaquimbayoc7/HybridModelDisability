# train_model.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
import joblib
import os

print("--- Iniciando Proceso de Entrenamiento Final (con snake_case) ---")

# --- 1. Simulación de Datos ALINEADA CON LA API (usando snake_case) ---
# CORRECCIÓN CRÍTICA: Los nombres de las columnas ahora están en snake_case.
data = {
    'edad': np.random.randint(18, 70, size=1000),
    'genero': np.random.choice(['Femenino', 'Masculino', 'No responde'], size=1000),
    'orientacion_sexual': np.random.choice(['Heterosexual', 'Homosexual', 'Bisexual', 'No responde'], size=1000),
    'causa_deficiencia': np.random.choice([
        "Enfermedad general", "Accidente de tránsito", "Alteración genética o hereditaria",
        "Complicaciones durante el parto", "Violencia por delincuencia común"
    ], size=1000),
    'cat_fisica': np.random.choice(['SI', 'NO'], size=1000),
    'cat_psicosocial': np.random.choice(['SI', 'NO'], size=1000),
    'nivel_d1': np.random.randint(0, 101, size=1000),
    'nivel_d2': np.random.randint(0, 101, size=1000),
    'nivel_d3': np.random.randint(0, 101, size=1000),
    'nivel_d4': np.random.randint(0, 101, size=1000),
    'nivel_d5': np.random.randint(0, 101, size=1000),
    'nivel_d6': np.random.randint(0, 101, size=1000),
    'nivel_global': np.random.randint(0, 101, size=1000),
}
df = pd.DataFrame(data)

# --- 2. Etapa de Clustering (Simulada) ---
cluster_vars = ['nivel_d1', 'nivel_d2', 'nivel_d3', 'nivel_d4']
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Perfil'] = kmeans.fit_predict(df[cluster_vars])

# --- 3. Etapa de Clasificación ---
print("Entrenando el modelo de clasificación final...")

# CORRECCIÓN CRÍTICA: La lista de características también usa snake_case.
feature_columns = [
    'edad', 'genero', 'orientacion_sexual', 'causa_deficiencia', 'cat_fisica',
    'cat_psicosocial', 'nivel_d1', 'nivel_d2', 'nivel_d3', 'nivel_d4',
    'nivel_d5', 'nivel_d6', 'nivel_global'
]
X = df[feature_columns]
y = df['Perfil']

numeric_features = X.select_dtypes(include=np.number).columns.tolist()
categorical_features = X.select_dtypes(include=['object']).columns.tolist()

preprocessor = ColumnTransformer(
    transformers=[
        ('num', MinMaxScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', GradientBoostingClassifier(random_state=42))
])

model_pipeline.fit(X, y)

# --- 4. Guardado del Modelo ---
model_dir = os.path.join(os.path.dirname(__file__))
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
model_path = os.path.join(model_dir, 'model_pipeline.joblib')
joblib.dump(model_pipeline, model_path)

print(f"✅ Modelo final guardado exitosamente en '{model_path}'")
print("Este modelo está ahora 100% alineado con la API (espera snake_case).")