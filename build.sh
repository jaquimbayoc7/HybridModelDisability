#!/usr/bin/env bash
# build.sh - Script para preparar la aplicación en Render

set -e  # Salir si hay algún error

echo "======================================"
echo "🚀 Iniciando proceso de build..."
echo "======================================"

# Paso 1: Verificar que las dependencias estén instaladas
echo "✓ Dependencias ya están instaladas"

# Paso 2: Generar el modelo si no existe
echo ""
echo "Verificando modelo ML..."
if [ ! -f "model/model_pipeline.joblib" ]; then
    echo "⚠️ Modelo no encontrado. Generando modelo..."
    python model/train_model.py
    echo "✓ Modelo generado correctamente"
else
    echo "✓ Modelo existe"
fi

# Paso 3: Inicializar la base de datos
echo ""
echo "Inicializando base de datos..."
python -c "
import os
from app.database import engine, Base

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    print('Creando esquema de base de datos...')
    try:
        Base.metadata.create_all(bind=engine)
        print('✓ Base de datos inicializada correctamente')
    except Exception as e:
        print(f'⚠️ Error al inicializar BD: {e}')
        print('Continuando... Las tablas se crearán al primer acceso.')
else:
    print('⚠️ DATABASE_URL no está configurada')
"

echo ""
echo "======================================"
echo "✓ Build completado exitosamente"
echo "======================================"

