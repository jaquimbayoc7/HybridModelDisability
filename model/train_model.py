import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
import joblib
import os

print("Iniciando el proceso de entrenamiento del modelo...")

# --- 1. Simulación de Datos ---
# En un caso real, cargarías tu CSV aquí.
# df = pd.read_csv('tus_datos.csv')
data = {
    # Variables para el K-Means (simulando Q13, Q14, etc.)
    'Barrier_1': np.random.randint(1, 5, size=1000),
    'Barrier_2': np.random.randint(1, 5, size=1000),
    'Barrier_3': np.random.randint(1, 5, size=1000),
    'Barrier_4': np.random.randint(1, 5, size=1000),

    # Variables para el clasificador (del formulario)
    'Edad': np.random.randint(18, 70, size=1000),
    'Genero': np.random.choice(['Femenino', 'Masculino', 'No responde'], size=1000),
    'Orientacion_Sexual': np.random.choice(['Heterosexual', 'No responde'], size=1000),
    'Causa_Deficiencia': np.random.choice([
        "Alteración genética o hereditaria", "Enfermedad general", "Accidente de tránsito",
        "Complicaciones durante el parto", "Alteraciones del desarrollo embrionario",
        "Accidente en el hogar", "Accidente de trabajo", "Violencia por delincuencia común"
    ], size=1000),
    'Cat_Fisica': np.random.choice(['SI', 'NO'], size=1000),
    'Cat_Psicosocial': np.random.choice(['SI', 'NO'], size=1000),
    'Nivel_D1': np.random.randint(0, 101, size=1000),
    'Nivel_D2': np.random.randint(0, 101, size=1000),
    'Nivel_D3': np.random.randint(0, 101, size=1000),
    'Nivel_D4': np.random.randint(0, 101, size=1000),
    'Nivel_D5': np.random.randint(0, 101, size=1000),
    'Nivel_D6': np.random.randint(0, 101, size=1000),
    'Nivel_Global': np.random.randint(0, 101, size=1000),
}
df = pd.DataFrame(data)

# --- 2. Etapa de Clustering (K-Means) ---
print("Ejecutando K-Means para generar las etiquetas de perfil...")
barrier_vars = ['Barrier_1', 'Barrier_2', 'Barrier_3', 'Barrier_4']
df_cluster = df[barrier_vars]
scaler_kmeans = MinMaxScaler()
df_cluster_scaled = scaler_kmeans.fit_transform(df_cluster)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Perfil'] = kmeans.fit_predict(df_cluster_scaled)
print(f"Perfiles generados: \n{df['Perfil'].value_counts()}\n")

# --- 3. Etapa de Clasificación (Gradient Boosting) ---
print("Entrenando el modelo de clasificación (Gradient Boosting)...")
feature_columns = [
    'Edad', 'Genero', 'Orientacion_Sexual', 'Causa_Deficiencia', 'Cat_Fisica',
    'Cat_Psicosocial', 'Nivel_D1', 'Nivel_D2', 'Nivel_D3', 'Nivel_D4',
    'Nivel_D5', 'Nivel_D6', 'Nivel_Global'
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
classification_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', GradientBoostingClassifier(random_state=42))
])
classification_pipeline.fit(X, y)

# --- 4. Guardado del Modelo ---
# El modelo se guardará dentro de la misma carpeta 'model'
model_path = os.path.join(os.path.dirname(__file__), 'model_pipeline.joblib')
joblib.dump(classification_pipeline, model_path)

print(f"✅ Modelo de clasificación guardado exitosamente en '{model_path}'")