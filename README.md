# 🧬 Hybrid Profiling API for Patients with Disabilities 🤖

[![Live API](https://img.shields.io/badge/API-Live-brightgreen)](https://hybridmodeldisability.onrender.com/docs)

This repository contains the source code for a RESTful API developed with FastAPI for patient management and disability profile classification using a hybrid Machine Learning model.

## 🔍 Overview

The API provides a secure and robust platform for medical staff to manage patient records. It includes token-based authentication (JWT), a role-based system (physician and admin), and a full suite of CRUD operations for patient data.

The core of the project is the integration of a Machine Learning model that uses a two-stage approach:
1.  **Clustering (K-Means):** To generate perception profiles based on barrier data.
2.  **Classification (Gradient Boosting):** To predict a patient's profile from their demographic and assessment data.

## ✨ Key Features

-   **Secure Authentication:** Registration and login for physicians with JWT access tokens.
-   **Patient Management (CRUD):** Full operations to create, read, update, and delete patient records.
-   **ML Model Integration:** A dedicated endpoint to run the model and predict a patient's profile.
-   **User Roles:**
    -   `physician`: Access to the patient CRUD and the prediction endpoint.
    -   `admin`: Access to list and manage the status (active/inactive) of physicians.
-   **Data Validation:** Robust and automatic data validation using Pydantic.
-   **Interactive Documentation:** Automatic generation of interactive API documentation with Swagger UI and ReDoc.
-   **Easy Deployment:** Configured for a straightforward deployment on platforms like Render.

## 🛠️ Tech Stack

-   **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
-   **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
-   **Machine Learning:** [Scikit-learn](https://scikit-learn.org/), [Pandas](https://pandas.pydata.org/), [Joblib](https://joblib.readthedocs.io/)
-   **Security & Passwords:** [Passlib](https://passlib.readthedocs.io/en/stable/) with `bcrypt`
-   **JWT Tokens:** [python-jose](https://github.com/mpdavis/python-jose)
-   **Data Validation:** [Pydantic](https://docs.pydantic.dev/latest/)

## 📂 Project Structure

```
/
├── app/
│   ├── main.py             # Main API entry point
│   ├── auth.py             # Authentication and JWT logic
│   ├── crud.py             # CRUD functions for the (simulated) database
│   ├── dependencies.py     # Dependencies for security and roles
│   ├── schemas.py          # Pydantic models for validation
│   └── routers/
│       ├── admin.py        # Endpoints for administrators
│       ├── patients.py     # Endpoints for patients
│       └── users.py        # Endpoints for registration and login
│
├── model/
│   ├── train_model.py      # Script to train and save the model
│   └── model_pipeline.joblib # Trained model file (generated)
│
├── .gitignore
└── requirements.txt
```

## 🚀 Local Installation and Execution

Follow these steps to get the project up and running on your local machine.

### 1. Prerequisites

-   Python 3.9 or higher.
-   Git.

### 2. Clone the Repository

```bash
git clone https://github.com/jaquimbayoc7/HybridModelDisability.git
cd HybridModelDisability
```

### 3. Create and Activate a Virtual Environment

It's a good practice to isolate project dependencies.

-   **Windows (CMD/PowerShell):**
    ```bash
    # Create the environment
    python -m venv venv
    # Activate the environment
    .\venv\Scripts\Activate.ps1
    ```

-   **macOS / Linux:**
    ```bash
    # Create the environment
    python3 -m venv venv
    # Activate the environment
    source venv/bin/activate
    ```

### 4. Install Dependencies

With the virtual environment activated, install all the necessary libraries.

```bash
pip install -r requirements.txt
```

### 5. Train the Machine Learning Model

This is a crucial one-time step. This script will generate the `model/model_pipeline.joblib` file that the API needs to function.

```bash
python model/train_model.py
```

### 6. Start the API

Everything is set! Start the development server.

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## 📖 API Usage

The easiest way to explore and test the API is through the interactive documentation.

-   **Live API Docs:** [**https://hybridmodeldisability.onrender.com/docs**](https://hybridmodeldisability.onrender.com/docs)
-   **Local Swagger UI:** `http://127.0.0.1:8000/docs`
-   **Local ReDoc:** `http://127.0.0.1:8000/redoc`

### Basic Workflow

1.  **Register a physician:** Use the `POST /users/register` endpoint.
2.  **Log in:** Use `POST /users/login` with the physician's email and password to get an `access_token`.
3.  **Authorize:** In the interactive documentation, click the "Authorize" button and paste the token in the format `Bearer <your_token>`.
4.  **Manage Patients:** You can now use all `/patients` endpoints to create, read, update, delete, and predict patient profiles.

### Example with `curl`

*(Note: You can replace `http://127.0.0.1:8000` with the live URL `https://hybridmodeldisability.onrender.com` in these examples)*

1.  **Login and get token:**
    ```bash
    curl -X POST "https://hybridmodeldisability.onrender.com/users/login" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=physician@example.com&password=password123"
    ```

2.  **Create a patient (using the obtained token):**
    ```bash
    TOKEN="your_access_token_here"

    curl -X POST "https://hybridmodeldisability.onrender.com/patients/" \
         -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -d '{
              "nombre_apellidos": "John Patient",
              "fecha_nacimiento": "1980-01-15",
              "edad": 44,
              "genero": "Masculino",
              "orientacion_sexual": "Heterosexual",
              "causa_deficiencia": "Accidente de trabajo",
              "cat_fisica": "SI",
              "cat_psicosocial": "NO",
              "nivel_d1": 50,
              "nivel_d2": 60,
              "nivel_d3": 70,
              "nivel_d4": 80,
              "nivel_d5": 90,
              "nivel_d6": 100,
              "nivel_global": 75
            }'
    ```

## ☁️ Deployment on Render

This project is fully configured for deployment on **Render** (platform as a service).

### Quick Start (Recommended)

For detailed deployment instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

### Key Points:
- **Build Command:** `pip install -r requirements.txt && bash build.sh`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Runtime:** Python 3.11
- **Required Environment Variables:**
  - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - `DATABASE_URL`: PostgreSQL connection string (provided by Render or your database)

### Critical Configuration:

1. **Use Internal Database URL**: Render PostgreSQL databases provide both internal and external URLs. **Always use the internal URL** (ending with `.internal`) in your Web Service.

2. **Same Region**: Ensure your Web Service and PostgreSQL database are in the **same region** for optimal performance.

3. **Automatic Initialization**: The build script automatically:
   - Trains the ML model if it doesn't exist
   - Creates database tables
   - Initializes the default admin user

### Troubleshooting:

If you encounter connection errors:
- Check `DATABASE_URL` format and that it uses the `.internal` domain
- Verify both services are in the same region
- Review Render logs: Dashboard → Web Service → Logs
- Clear cache and redeploy: Dashboard → Web Service → Settings → "Clear Cache & Redeploy"

---

## 👥 Authors

-   **Julian Andres Quimbayo Castro** - [julian.quimbayo@corhuila.edu.co](mailto:julian.quimbayo@corhuila.edu.co)
-   **Willians Aguilar Rodriguez** - [waguilar-2021a@corhuila.edu.co](mailto:waguilar-2021a@corhuila.edu.co)
-   **Jose Miguel Llanos Mosquera** - [jmllanosm@corhuila.edu.co](mailto:jmllanosm@corhuila.edu.co)
-   **Cindy Vargas Duque** - [sistemas@corhuila.edu.co](mailto:sistemas@corhuila.edu.co)
