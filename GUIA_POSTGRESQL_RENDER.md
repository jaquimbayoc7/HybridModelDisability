# 🔧 Guía Paso a Paso: PostgreSQL y Variables de Entorno en Render

## 📋 ÍNDICE
1. [Generar SECRET_KEY](#1-generar-secret_key)
2. [Crear Base de Datos PostgreSQL](#2-crear-base-de-datos-postgresql)
3. [Obtener Credenciales de la BD](#3-obtener-credenciales-de-la-bd)
4. [Crear Web Service](#4-crear-web-service)
5. [Configurar Variables de Entorno](#5-configurar-variables-de-entorno)
6. [Conectar BD con Web Service](#6-conectar-bd-con-web-service)
7. [Verificar la Conexión](#7-verificar-la-conexión)

---

## 1. Generar SECRET_KEY

Una `SECRET_KEY` es necesaria para firmar los tokens JWT de autenticación.

### Opción A: Desde Windows PowerShell

```powershell
# En PowerShell activado del proyecto
.\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Salida esperada:**
```
Z3x8kP9mQ2xJ7wL-5vN_8qM3zR4yT6uC
```

### Opción B: Desde terminal en línea

Puedes usar cualquiera de estas opciones online:
- [Random String Generator](https://www.random.org/strings/)
- Copiar y generar algo como: `aBcDeF1234567890GhIjKlMnOpQrStUvWxYz`

**✅ Guarda este valor en algún lugar seguro, lo necesitarás después.**

---

## 2. Crear Base de Datos PostgreSQL

### Paso 2.1: Ir a Render Dashboard

1. Ve a [render.com](https://render.com)
2. **Inicia sesión** con tu cuenta (crea una si no tienes)
3. En el dashboard, haz clic en **"New +"** (esquina superior derecha)
4. Selecciona **"PostgreSQL"**

### Paso 2.2: Configurar la Base de Datos

Rellena el formulario con:

| Campo | Valor |
|-------|-------|
| **Name** | `disability-api-db` |
| **Database** | `disability_db` |
| **User** | `(auto-generado, dejar igual)` |
| **Region** | `Elige la más cercana a ti` *(IMPORTANTE)* |
| **PostgreSQL Version** | `15` |

<img src="https://i.imgur.com/placeholder.png" alt="Formulario PostgreSQL" width="400">

**⚠️ IMPORTANTE: La región debe ser la MISMA que uses para el Web Service**

### Paso 2.3: Crear la Base de Datos

Haz clic en **"Create Database"** y espera 2-3 minutos.

Verás un mensaje: **"Database is ready"** ✅

---

## 3. Obtener Credenciales de la BD

### Paso 3.1: Copiar la Internal Database URL

Una vez que la BD está lista:

1. En el dashboard de Render, haz clic en tu base de datos **"disability-api-db"**
2. En la sección **"Connections"**, verás varias opciones:
   - **External Database URL** ← ❌ NO USES ESTO
   - **Internal Database URL** ← ✅ USA ESTO
   - **PSQL Command** 
   - **Connection Properties**

3. **Copia el "Internal Database URL"**

**Ejemplo:**
```
postgresql://vxwzpd_user:AbCdEfGhIjKl@dpg-cl8c9v2l7s3e00d3mpa0-a.internal:5432/vxwzpd_db
```

### Paso 3.2: Convertir el URL

El URL que copiaste comienza con `postgresql://`, pero Render requiere `postgresql+psycopg2://`.

**Reemplaza:**
```
postgresql:// → postgresql+psycopg2://
```

**Ejemplo transformado:**
```
postgresql+psycopg2://vxwzpd_user:AbCdEfGhIjKl@dpg-cl8c9v2l7s3e00d3mpa0-a.internal:5432/vxwzpd_db
```

<details>
<summary>👉 Haz clic aquí si necesitas ayuda para identificar las partes del URL</summary>

```
postgresql+psycopg2://usuario:contraseña@host:puerto/base_de_datos
                      ↓         ↓          ↓     ↓    ↓
                    vxwzpd_user AbCdEf... dpg... 5432 vxwzpd_db
```

- **usuario**: Lo que está antes de `:` 
- **contraseña**: Lo que está entre `:` y `@`
- **host**: Lo que está entre `@` y `:` (debe terminar en `.internal`)
- **puerto**: `5432` (estándar PostgreSQL)
- **base_de_datos**: Lo que está después del último `/`

</details>

---

## 4. Crear Web Service

### Paso 4.1: Conectar tu Repositorio

1. En Render Dashboard, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Selecciona **"GitHub"** (conecta Render con GitHub si no está conectado)
4. Busca `HybridModelDisability` y selecciónalo
5. Haz clic en **"Connect"**

### Paso 4.2: Configurar el Web Service

Rellena el formulario:

| Campo | Valor |
|-------|-------|
| **Name** | `hybrid-disability-api` |
| **Environment** | `Python 3` |
| **Region** | **LA MISMA QUE LA BD** *(muy importante)* |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt && bash build.sh` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Autodeployed from active branches?** | Marcar ✅ |

### Paso 4.3: No despliegues aún

**Haz clic en "Create Web Service"**, pero verá que fallará porque faltan las variables de entorno.

Continuaremos en el siguiente paso.

---

## 5. Configurar Variables de Entorno

### Paso 5.1: Ir a Environment Variables

En tu Web Service `hybrid-disability-api`:

1. En el panel izquierdo, busca **"Environment"**
2. Haz clic en **"Environment Variables"**

### Paso 5.2: Agregar SECRET_KEY

1. Haz clic en **"Add Environment Variable"**
2. Rellena:
   - **Key**: `SECRET_KEY`
   - **Value**: `(La clave que generaste en el Paso 1)`

3. Haz clic en **"Save"**

**Ejemplo:**
```
Key:   SECRET_KEY
Value: Z3x8kP9mQ2xJ7wL-5vN_8qM3zR4yT6uC
```

### Paso 5.3: Agregar DATABASE_URL

Este paso lo harías manualmente O puedes conectar automáticamente con la BD.

#### OPCIÓN 1: Conexión Automática (Recomendada)

1. En el Web Service, sección **"Connected Services"**
2. Haz clic en **"Connect to PostgreSQL Database"** o **"Add a service"**
3. Selecciona tu BD `disability-api-db`
4. Render **automáticamente** agregará `DATABASE_URL`

#### OPCIÓN 2: Manual

Si la opción anterior no funciona:

1. Haz clic en **"Add Environment Variable"** nuevamente
2. Rellena:
   - **Key**: `DATABASE_URL`
   - **Value**: `(El URL convertido del Paso 3.2)`

**Ejemplo:**
```
Key:   DATABASE_URL
Value: postgresql+psycopg2://vxwzpd_user:AbCdEfGhIjKl@dpg-cl8c9v2l7s3e00d3mpa0-a.internal:5432/vxwzpd_db
```

3. Haz clic en **"Save"**

---

## 6. Conectar BD con Web Service

### Paso 6.1: Verificar la Conexión

En tu BD `disability-api-db`:

1. Haz clic en la BD
2. En la sección **"Data Access"**, verás:
   - Static IPs: (deja vacío si es gratis)
   - Trust proxy headers: (pueden dejado como está)

### Paso 6.2: Verificar que están en la MISMA REGIÓN

Este es el paso más importante que la gente olvida:

1. **Abre 2 ventanas:**
   - Pestaña 1: Tu BD `disability-api-db` → Region
   - Pestaña 2: Tu Web Service `hybrid-disability-api` → Environment → Region

2. **Verifica que AMBAS digan la misma región**

**Ejemplo correcto:**
```
BD:         Region: Singapore (sgp-1)
Web Service: Region: Singapore (sgp-1)
✅ ¡Coinciden!
```

**Ejemplo incorrecto (esto NO funcionará):**
```
BD:         Region: Ohio (ohi)
Web Service: Region: Singapore (sgp-1)
❌ ¡Están en regiones diferentes!
```

Si están diferentes:

#### Solución A: Cambiar BD a la región del Web Service
1. En BD: Settings (engranaje) → Change Region
2. Selecciona la región del Web Service
3. Haz clic en "Change Region"

#### Solución B: Cambiar Web Service a la región de la BD
1. En Web Service: Settings → Region
2. Selecciona la región de la BD
3. Guarda cambios

---

## 7. Verificar la Conexión

### Paso 7.1: Forzar un Redeploy

En tu Web Service:

1. Haz clic en **"Settings"** (engranaje)
2. Baja hasta **"Deployment"**
3. Haz clic en **"Clear Cache & Deploy"**

Espera 3-5 minutos mientras Render:
- Descarga tu código
- Instala dependencias
- Ejecuta `build.sh` (que entrena el modelo y crea tablas)
- Inicia el servidor

### Paso 7.2: Ver los Logs

En tu Web Service, sección **"Logs"** (línea de tiempo en vivo):

**Busca estas líneas (indicativo de éxito):**

```
✓ Dependencias ya están instaladas
✓ Modelo existe
Inicializando base de datos...
Creando esquema de base de datos...
✓ Base de datos inicializada correctamente
✓ Usuario administrador por defecto creado.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Si ves estos errores, revisar soluciones:**

| Error | Causa | Solución |
|-------|-------|----------|
| `could not translate host name "dpg-..." to address` | BD no accesible | Verificar región, usar `.internal` URL |
| `relation "users" does not exist` | Tablas no creadas | Ver logs de `build.sh` |
| `FATAL: password authentication failed` | Credenciales incorrectas | Copiar URL exactamente desde Render |

### Paso 7.3: Probar la API

Una vez que ves **"Uvicorn running"**:

1. Copia la URL de tu Web Service (algo como `https://hybrid-disability-api.onrender.com`)
2. Abre en navegador: `https://hybrid-disability-api.onrender.com/docs`
3. Deberías ver la documentación interactiva de Swagger

**Si ves esto, ¡todo está funcionando!** ✅

---

## 📋 Checklist Final

Antes de dar por completado:

- [x] Generé `SECRET_KEY` segura
- [x] Creé BD PostgreSQL en Render
- [x] Copié y convertí el URL (`postgresql+psycopg2://`)
- [x] Creé Web Service
- [x] Configuré `SECRET_KEY` variable de entorno
- [x] Configuré `DATABASE_URL` variable de entorno
- [x] BD y Web Service están en la **MISMA REGIÓN**
- [x] Ejecuté "Clear Cache & Deploy"
- [x] Vi los logs de startup correctamente
- [x] Accedí a `/docs` en la URL del Web Service

---

## 🆘 Troubleshooting

### "Database connection refused"

```
Soluciones:
1. Verificar que DATABASE_URL está exactamente igual al que Render proporciona
2. Verificar que usa .internal (NO .render.com)
3. Verificar que BD y Web Service están en MISMA REGIÓN
4. Esperar 5 minutos adicionales (a veces tarda en conectar)
5. Hacer "Clear Cache & Deploy" nuevamente
```

### "FATAL: Ident authentication failed"

```
Significa que la contraseña está mal. Soluciones:
1. Ir a BD → Connections → Internal Database URL
2. Copiar EXACTAMENTE el URL completo
3. Reemplazar postgresql:// por postgresql+psycopg2://
4. Pegar en Environment Variables → DATABASE_URL
5. Hacer "Clear Cache & Deploy"
```

### "relation does not exist"

```
Las tablas no se creatron. Ver logs Buscar: "Create schema"

Si dice "Error al inicializar BD:", el modelo ML no está generado:
1. Git push nuevamente con model/model_pipeline.joblib generado
2. O en Web Service settings: "Clear Cache & Deploy"
```

---

## 🎯 Resumen de URLs y Conceptos

| Tipo | Ejemplo | Uso |
|------|---------|-----|
| External DB URL | `postgresql://user@dpg-xx.render.com` | ❌ NO USAR |
| Internal DB URL | `postgresql://user@dpg-xx.internal` | ✅ USAR (convertir a psycopg2) |
| Web Service URL | `https://app-name.onrender.com` | ✅ USAR para acceder |
| PSQL Command | `psql postgresql://...` | CLI, no es necesario |

---

**¿Necesitas ayuda? Revisa los logs de tu Web Service en Render Dashboard.**
