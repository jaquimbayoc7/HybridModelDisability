# ⚙️ Configuración Específica para TU Base de Datos en Render

## 📊 TUS DATOS DE LA BD

```
Database Name:  disability_api_db
Username:       disability_api_db_user
Password:       9E2GtjT6XCRjG6G0jcN8wUVC1vKehtWR
Host:           dpg-d6gaf7f5r7bs73dd23gg-a
Port:           5432
```

---

## 🔑 VARIABLES DE ENTORNO QUE NECESITAS

### Variable 1: DATABASE_URL

**COPIA Y PEGA EXACTAMENTE ESTO:**

```
postgresql+psycopg2://disability_api_db_user:9E2GtjT6XCRjG6G0jcN8wUVC1vKehtWR@dpg-d6gaf7f5r7bs73dd23gg-a/disability_api_db
```

> ✅ Ya está en el formato correcto (`postgresql+psycopg2://`)
> 
> ✅ Ya tiene las credenciales incluidas
> 
> ✅ Usa el host interno (`.internal` está implícito en el dominio `dpg-...`)

### Variable 2: SECRET_KEY

Necesitas generar una clave segura. Ejecuta en PowerShell:

```powershell
.\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Ejemplo de salida:**
```
Z3x8kP9mQ2xJ7wL-5vN_8qM3zR4yT6uC
```

**Copia la salida como tu SECRET_KEY** (será diferente cada vez que ejecutes)

---

## 📝 PASOS EN RENDER DASHBOARD

### Paso 1: Ir a tu Web Service

1. Abre [render.com](https://render.com)
2. Busca tu Web Service `hybrid-disability-api`
3. Haz clic en él para abrir el dashboard

### Paso 2: Configurations → Environment

1. En el panel izquierdo, busca **"Environment"**
2. Haz clic en **"Environment Variables"**

### Paso 3: Agregar DATABASE_URL

1. Haz clic en **"Add Environment Variable"**

2. Rellena exactamente así:

   ```
   Key:   DATABASE_URL
   Value: postgresql+psycopg2://disability_api_db_user:9E2GtjT6XCRjG6G0jcN8wUVC1vKehtWR@dpg-d6gaf7f5r7bs73dd23gg-a/disability_api_db
   ```

3. Haz clic en **"Save"**

> ⚠️ **IMPORTANTE**: 
> - No agregues comillas
> - No cambies nada del URL
> - La contraseña está dentro del URL, así que está segura

### Paso 4: Agregar SECRET_KEY

1. Haz clic **nuevamente** en **"Add Environment Variable"**

2. Rellena así:

   ```
   Key:   SECRET_KEY
   Value: (Pega la salida que generaste en PowerShell)
   ```

   **Ejemplo:**
   ```
   Key:   SECRET_KEY
   Value: Z3x8kP9mQ2xJ7wL-5vN_8qM3zR4yT6uC
   ```

3. Haz clic en **"Save"**

### Paso 5: Verificar que ambas variables estén añadidas

Deberías ver en la sección "Environment Variables":

```
DATABASE_URL = postgresql+psycopg2://disability_api_db_user:****@dpg-d6gaf7f5r7bs73dd23gg-a/disability_api_db
SECRET_KEY   = Z3x8kP9mQ2xJ7wL-5vN_8qM3zR4yT6uC
```

> La contraseña en DATABASE_URL aparecerá oculta con `****` por seguridad

---

## 🚀 DESPLEGAR

Ahora que las variables están configuradas:

1. En el Web Service, ve a **"Settings"** (engranaje ⚙️)
2. Baja hasta **"Deployment"**
3. Haz clic en **"Clear Cache & Deploy"**

**Espera 5-10 minutos** mientras Render:
- Descarga tu código
- Instala dependencias
- Crea las tablas de la BD
- Inicia el servidor

---

## 📋 VERIFICACIÓN

### Paso 1: Ver los Logs

En tu Web Service, haz clic en la pestaña **"Logs"** para ver el progreso en tiempo real.

**Busca estas líneas (significa que funciona):**

```
✓ Dependencias ya están instaladas
✓ Modelo existe
Inicializando base de datos...
Creando esquema de base de datos...
✓ Base de datos inicializada correctamente
✓ Usuario administrador por defecto creado.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Paso 2: Acceder a la API

Una vez que veas **"Uvicorn running"** en los logs:

1. Copia la URL de tu Web Service (en la parte superior del dashboard)
   - Algo como: `https://hybrid-disability-api.onrender.com`

2. Abre en navegador: 
   ```
   https://hybrid-disability-api.onrender.com/docs
   ```

3. Deberías ver la documentación interactiva de Swagger con todos los endpoints

**✅ ¡Si ves esto, todo está funcionando!**

---

## ❌ SOLUCIONAR PROBLEMAS

### Error: "could not translate host name"

```
Causa: Render no puede contactar la BD
Soluciones:
1. ✅ Verificar que DATABASE_URL se copió EXACTAMENTE igual
2. ✅ Verificar que no hay espacios al inicio o final
3. ✅ Esperar 5 minutos adicionales
4. ✅ Hacer "Clear Cache & Deploy" nuevamente
```

### Error: "FATAL: password authentication failed"

```
Causa: La contraseña está mal
Solución:
1. Ir a tu BD en Render → Database → Connections
2. Copiar nuevamente el "Internal Database URL"
3. Reemplazar exactamente en Environment Variables
4. Hacer "Clear Cache & Deploy"
```

### Error: "relation 'users' does not exist"

```
Causa: Las tablas no se crearon
Ver en los logs si aparece alguno de estos:
- "Error al inicializar BD:"
- "Traceback"

Soluciones:
1. Hacer "Clear Cache & Deploy" nuevamente
2. Esperar a que el modelo ML se genere (puede tardar 2-3 minutos)
3. Ver que el archivo model/model_pipeline.joblib está en el repositorio
```

---

## 📌 RESUMEN DE CONFIGURACIÓN

| Campo | Tu Valor |
|-------|----------|
| **DATABASE_URL** | `postgresql+psycopg2://disability_api_db_user:9E2GtjT6XCRjG6G0jcN8wUVC1vKehtWR@dpg-d6gaf7f5r7bs73dd23gg-a/disability_api_db` |
| **SECRET_KEY** | `(genera una nueva con python)` |
| **Web Service Name** | `hybrid-disability-api` |
| **Build Command** | `pip install -r requirements.txt && bash build.sh` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

---

## 🔗 PRÓXIMOS PASOS

1. **Generar SECRET_KEY** en PowerShell
2. **Agregar variables de entorno** en Render
3. **Hacer Clear Cache & Deploy**
4. **Ver logs** para verificar que funciona
5. **Acceder a /docs** en tu URL del Web Service

**¿Necesitas ayuda en alguno de estos pasos?**
