# Health Tracker API

This is a RESTful API for a Health Tracker Application, built with FastAPI and SQLAlchemy. It allows users to track and analyze their health data, including Physical Activity, Sleep Activity, and Blood Tests. It also provides an aggregation endpoint to calculate a user's health score and demonstrates integration with an external FHIR-based API.

## Features

- User Management: Basic CRUD operations for user accounts.
- Health Data Management: CRUD operations for Physical Activity, Sleep Activity, and Blood Test records.
- Health Score Calculation: An endpoint to aggregate health data, calculate a health score, and compare it to other users in the system.
- FHIR Compliant Output: Health scores are returned in a FHIR-compliant Observation resource format.
- External FHIR API Integration: Example endpoint to fetch Patient resources from a public FHIR API.

## Database Schema

The application uses a PostgreSQL relational database with the following tables:

- `users`: Stores user information (id, username, email, password).
- `physical_activities`: Stores physical activity records (id, user_id, activity_type, duration_minutes, calories_burned, date).
- `sleep_activities`: Stores sleep activity records (id, user_id, sleep_duration_hours, sleep_quality, date).
- `blood_tests`: Stores blood test records (id, user_id, test_name, test_result, units, date).

## Setup and Installation

Follow these steps to set up and run the Health Tracker API locally.

### Prerequisites

- Python 3.9+ (or the version you provided: Python313)
- PostgreSQL database server

### 1. Clone the repository (if applicable) and navigate to the project directory

```bash
git clone <your-repository-url>
cd health_tracker_api
```

### 2. Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# On Windows
<path_to_your_python_executable> -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Replace `<path_to_your_python_executable>` with the actual path you provided (e.g., `C:\Users\USER\AppData\Local\Programs\Python\Python313\python.exe`).

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Database Connection

Open `database.py` and update the `SQLALCHEMY_DATABASE_URL` with your PostgreSQL database connection string. Make sure the database `health_tracker_db` exists on your PostgreSQL server.

```python
# database.py
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/health_tracker_db"
```

### 5. Run the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

Once the application is running, you can access the API documentation (Swagger UI) at `http://127.0.0.1:8000/docs` to test the endpoints.

### User Endpoints

- `POST /users/`: Create a new user.
- `GET /users/`: Get a list of all users.
- `GET /users/{user_id}`: Get a specific user by ID.
- `PUT /users/{user_id}`: Update an existing user.
- `DELETE /users/{user_id}`: Delete a user.

### Physical Activity Endpoints

- `POST /users/{user_id}/physical_activities/`: Create a new physical activity record for a user.
- `GET /users/{user_id}/physical_activities/`: Get all physical activity records for a user.
- `GET /physical_activities/{activity_id}`: Get a specific physical activity record by ID.
- `PUT /physical_activities/{activity_id}`: Update a physical activity record.
- `DELETE /physical_activities/{activity_id}`: Delete a physical activity record.

### Sleep Activity Endpoints

- `POST /users/{user_id}/sleep_activities/`: Create a new sleep activity record for a user.
- `GET /users/{user_id}/sleep_activities/`: Get all sleep activity records for a user.
- `GET /sleep_activities/{sleep_id}`: Get a specific sleep activity record by ID.
- `PUT /sleep_activities/{sleep_id}`: Update a sleep activity record.
- `DELETE /sleep_activities/{sleep_id}`: Delete a sleep activity record.

### Blood Test Endpoints

- `POST /users/{user_id}/blood_tests/`: Create a new blood test record for a user.
- `GET /users/{user_id}/blood_tests/`: Get all blood test records for a user.
- `GET /blood_tests/{blood_test_id}`: Get a specific blood test record by ID.
- `PUT /blood_tests/{blood_test_id}`: Update a blood test record.
- `DELETE /blood_tests/{blood_test_id}`: Delete a blood test record.

### Health Score Endpoint

- `GET /users/{user_id}/get_health_score`: Calculate and retrieve the health score for a user.

### External FHIR API Endpoint

- `GET /fhir_patient/{patient_id}`: Fetch a Patient resource from a public FHIR API.
