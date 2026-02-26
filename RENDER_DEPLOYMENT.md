# 🚀 Guía de Despliegue en Render

## Paso 1: Preparar el Repositorio

Asegúrate de que estos archivos estén en el repositorio:
- `Procfile` ✓ (creado)
- `runtime.txt` ✓ (creado)
- `requirements.txt` ✓ (actualizado)
- `build.sh` ✓ (creado)
- `render.yaml` ✓ (creado)

## Paso 2: Variables de Entorno Críticas en Render

En el dashboard de Render, debes configurar estas variables de entorno:

### 2.1 - OPCIÓN A: Deployment Manual (Recomendado)

1. Crea un nuevo **Web Service** en Render:
   - Conecta tu repositorio GitHub
   - Nombre: `hybrid-disability-api`
   - Runtime: `Python 3.11`
   - Build Command: `pip install -r requirements.txt && bash build.sh`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. Agrega estas **Environment Variables** en Render:

   ```
   SECRET_KEY=una-clave-muy-segura-aqui (genera una con: python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

3. Crea una **PostgreSQL Database** en Render:
   - Nombre: `disability-api-db`
   - Version: 15
   - Toma nota del `Internal Database URL`

4. Copia el `Internal Database URL` y configúralo en tu Web Service:
   
   - Si comienza con `postgresql://`, cámbialo a: `postgresql+psycopg2://...`
   
   Ejemplo:
   ```
   postgresql+psycopg2://user:password@dpg-xxxxx.render.internal:5432/dbname
   ```

   **⚠️ IMPORTANTE**: Debe usar el `.internal` URL, NO el URL externo.

### 2.2 - OPCIÓN B: Usar Infrastructure as Code (render.yaml)

1. En Render, selecciona **"Create" > "Create from GitHub"**
2. Selecciona tu repositorio
3. Elige **"Deploy with render.yaml"**
4. Render creará automáticamente el Web Service y la BD PostgreSQL

## Paso 3: Solucionar Errores de Conexión

### Error: "could not translate host name... to address"

**Causas comunes:**
1. La Base de datos está en una región diferente del Web Service
2. Estás usando el URL externo en lugar del URL interno
3. Las credenciales son incorrectas

**Soluciones:**
1. Verifica que ambos servicios estén en la **misma región**
2. Usa siempre el **Internal Database URL** (terminación `.internal`)
3. Reinicia el Web Service después de cambiar variables de entorno

### Error: "relation does not exist"

Esto significa que las tablas no se crearon. Soluciones:

1. **Manual**: Ve a los Logs del Web Service, busca líneas que comiencen con `✓` o `⚠`
2. **Re-ejecutar build**: En Render Dashboard, haz clic en **"Clear Cache & Redeploy"**
3. **Ejecutar manualmente**:
   ```bash
   # En los logs de Render o localmente con la BD remota:
   python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

## Paso 4: Verificar que Funciona

1. Abre `https://your-app.onrender.com/docs` en tu navegador
2. Deberías ver la documentación interactiva de Swagger
3. Intenta el endpoint `GET /` que devuelve un mensaje de bienvenida

## Paso 5: Crear el Usuario Admin

Si el usuario admin no se crea automáticamente:

1. Usa el endpoint `POST /admin/users/register` con:
   ```json
   {
     "email": "administrador@salud.co",
     "password": "adminpassword",
     "full_name": "Administrador del Sistema",
     "role": "admin"
   }
   ```

## Troubleshooting Avanzado

### Ver los logs en tiempo real:
```bash
# En Render, haz clic en "Logs" en el dashboard
# Busca líneas que indiquen el estado de la inicialización
```

### Verificar conectividad de la BD:
```bash
# Si tienes acceso SSH (en el Web Service):
psql "postgresql+psycopg2://user:password@host:5432/db" -c "SELECT 1;"
```

### Forzar reconstrucción completa:
En el Render Dashboard:
1. Vaya a la configuración del Web Service
2. Haga clic en **"Clear Cache & Redeploy"**

## URLs Importantes

- Docs API: `https://your-app.onrender.com/docs`
- ReDoc: `https://your-app.onrender.com/redoc`
- Root: `https://your-app.onrender.com/`

---

**¿Aún tienes problemas?** Verifica:
- [ ] `DATABASE_URL` está configurada con URL `.internal`
- [ ] `SECRET_KEY` está configurada
- [ ] Web Service y DB están en la **misma región**
- [ ] Archivos `build.sh`, `Procfile`, `runtime.txt` existen en el repo
