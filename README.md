# Health Tracker App

This is a comprehensive Health Tracker Application built with a microservices architecture using FastAPI. It allows users to track and analyze their health data, including Physical Activity, Sleep Activity, and Blood Tests. The application provides health score calculations, statistics, and integrates with external FHIR-based APIs.

## Architecture Overview

The application is built using a microservices architecture with 6 independent services:

1. **API Gateway** - Single entry point for all client requests
2. **User Service** - Manages user accounts and authentication
3. **Reference Data Service** - Manages activity types and blood test units
4. **Health Data Service** - Manages physical activities, sleep, and blood tests
5. **Analytics Service** - Calculates health scores and statistics
6. **Integration Service** - Handles external FHIR API integration

## Features

- **User Management**: Complete CRUD operations for user accounts
- **Health Data Tracking**: Record and manage physical activities, sleep patterns, and blood test results
- **Health Score Calculation**: Advanced algorithms to calculate overall health scores based on multiple factors
- **Activity Statistics**: Detailed analytics for daily, weekly, and monthly activity patterns
- **FHIR Integration**: External API integration for healthcare data standards

## Database Schema

All services share a single PostgreSQL database (`health_tracker_db`) with the following tables:

- **User Service**: `users` table (id, username, email, password)
- **Reference Data Service**: `activity_types`, `blood_test_units` tables
- **Health Data Service**: 
  - `physical_activities` (id, user_id, activity_type_id, duration, calories, date, timestamp)
  - `sleep_activities` (id, user_id, hours, quality, date)
  - `blood_tests` (id, user_id, test_name, value, units_id, date)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Application

1. **Clone and navigate to the project**:
   ```bash
   git clone https://github.com/KH1729/healthTrackerApp
   cd healthTrackerApp
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Check service status**:
   ```bash
   docker-compose ps
   ```

4. **Access the application**:
   - **API Gateway**: http://localhost:8080
   - **API Documentation**: http://localhost:8080/docs
   - **Health Checks**: Each service has `/health` endpoint

### Service Ports (for debugging)

- **API Gateway**: 8080
- **User Service**: 8001
- **Reference Data Service**: 8002
- **Health Data Service**: 8003
- **Analytics Service**: 8004
- **Integration Service**: 8005

### Database Access

- **Shared Database**: localhost:5432
- **Database Name**: health_tracker_db
- **Username**: user
- **Password**: password

## API Endpoints

### User Management
- `POST /users/` - Create a new user
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get specific user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Reference Data
- `POST /activity_types/` - Create activity type
- `GET /activity_types/` - List activity types
- `POST /blood_test_units/` - Create blood test unit
- `GET /blood_test_units/` - List blood test units

### Health Data
- `POST /physical_activities/` - Create physical activity
- `GET /users/{user_id}/physical_activities/` - Get user's activities
- `POST /sleep_activities/` - Create sleep activity
- `GET /users/{user_id}/sleep_activities/` - Get user's sleep data
- `POST /blood_tests/` - Create blood test
- `GET /users/{user_id}/blood_tests/` - Get user's blood tests

### Analytics
- `GET /users/{user_id}/get_health_score` - Calculate health score
- `GET /users/{user_id}/physical_activities/stats/last_day` - Daily statistics
- `GET /users/{user_id}/physical_activities/stats/last_week` - Weekly statistics
- `GET /users/{user_id}/physical_activities/stats/last_month` - Monthly statistics

### External Integration
- `GET /fhir_patient/{patient_id}` - Fetch FHIR patient data

## Development

### Service Communication

Services communicate via HTTP calls with validation:
```python
# Example: Health Data Service validates user exists
async def validate_user(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
```

### Local Development

For individual service development:
```bash
# Run specific service locally
cd user-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Health Score Calculation

The analytics service calculates health scores based on:
- **Physical Activity**: Duration and calories burned
- **Sleep Quality**: Hours of sleep and quality metrics
- **Blood Test Results**: Medical test values and trends

Scores are normalized to 0-100 scale with personalized recommendations.

## Monitoring

### Health Checks
Each service provides health monitoring:
```bash
curl http://localhost:8080/health
```

### Logs
View service logs:
```bash
docker-compose logs -f [service-name]
```

## FHIR Integration

The integration service connects to external FHIR servers:
- **Patient Resources**: Fetch patient information
- **Observation Resources**: Health score output in FHIR format
- **Error Handling**: Graceful degradation when external services are unavailable

### Configuring New FHIR Connections

The FHIR integration is configured through environment variables in the `integration-service`. Here's how to add new FHIR server connections:

#### Method 1: Environment Variables (Recommended)

Add FHIR configuration to your `docker-compose.yml`:

```yaml
integration-service:
  build: ./integration-service
  environment:
    FHIR_SERVER_URL: https://your-fhir-server.com/baseR4
    FHIR_REQUEST_TIMEOUT: 30
    FHIR_MAX_RETRIES: 3
```

#### Method 2: Multiple FHIR Servers

For multiple FHIR servers, you can configure them using different environment variables:

```yaml
integration-service:
  build: ./integration-service
  environment:
    # Primary FHIR server
    FHIR_SERVER_URL: https://primary-fhir-server.com/baseR4
    FHIR_REQUEST_TIMEOUT: 30
    FHIR_MAX_RETRIES: 3
    
    # Secondary FHIR server (for failover)
    FHIR_SERVER_URL_BACKUP: https://backup-fhir-server.com/baseR4
    FHIR_REQUEST_TIMEOUT_BACKUP: 45
    FHIR_MAX_RETRIES_BACKUP: 5
```

#### Method 3: Authentication

For FHIR servers requiring authentication, add the necessary headers:

```yaml
integration-service:
  build: ./integration-service
  environment:
    FHIR_SERVER_URL: https://secure-fhir-server.com/baseR4
    FHIR_REQUEST_TIMEOUT: 30
    FHIR_MAX_RETRIES: 3
    FHIR_AUTH_TOKEN: your-access-token
    FHIR_API_KEY: your-api-key
```

#### Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `FHIR_SERVER_URL` | `https://hapi.fhir.org/baseR4` | FHIR server base URL |
| `FHIR_REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `FHIR_MAX_RETRIES` | `3` | Maximum retry attempts |
| `FHIR_AUTH_TOKEN` | `None` | OAuth2 access token |
| `FHIR_API_KEY` | `None` | API key for authentication |

#### Testing FHIR Connections

1. **Test basic connectivity**:
   ```bash
   curl http://localhost:8080/fhir_patient/example
   ```

2. **Test with your FHIR server**:
   ```bash
   curl http://localhost:8080/fhir_patient/your-patient-id
   ```

3. **Check FHIR server status**:
   ```bash
   curl http://localhost:8080/fhir_server_status
   ```

#### Common FHIR Server URLs

- **HAPI FHIR (Public)**: `https://hapi.fhir.org/baseR4`
- **HAPI FHIR (Test)**: `https://test.fhir.org/baseR4`
- **Microsoft FHIR**: `https://your-tenant.azurehealthcareapis.com`
- **AWS HealthLake**: `https://your-healthlake.region.amazonaws.com`
- **Google Healthcare API**: `https://healthcare.googleapis.com/v1/projects/your-project/locations/your-location/datasets/your-dataset/fhirStores/your-store`

#### Error Handling

The FHIR integration includes robust error handling:
- **Timeout handling**: Configurable timeouts with retry logic
- **Authentication errors**: Proper handling of 401/403 responses
- **Network errors**: Graceful degradation when servers are unavailable
- **Data parsing**: Safe parsing of FHIR responses with fallback values

#### Customizing FHIR Data Parsing

To customize how FHIR data is parsed, modify the `parse_fhir_patient` function in `integration-service/app/main.py`:

```python
def parse_fhir_patient(fhir_data: Dict[str, Any], patient_id: str) -> FHIRPatientResponse:
    # Customize parsing logic here
    # Add your specific FHIR resource handling
    pass
```

