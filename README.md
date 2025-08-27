# Health Tracker App - Microservices Architecture

This is a comprehensive Health Tracker Application built with a microservices architecture using FastAPI. It allows users to track and analyze their health data, including Physical Activity, Sleep Activity, and Blood Tests. The application provides health score calculations, statistics, and integrates with external FHIR-based APIs.

## 🏗️ Architecture Overview

The application is built using a microservices architecture with 6 independent services:

1. **API Gateway** - Single entry point for all client requests
2. **User Service** - Manages user accounts and authentication
3. **Reference Data Service** - Manages activity types and blood test units
4. **Health Data Service** - Manages physical activities, sleep, and blood tests
5. **Analytics Service** - Calculates health scores and statistics
6. **Integration Service** - Handles external FHIR API integration

## ✨ Features

- **User Management**: Complete CRUD operations for user accounts
- **Health Data Tracking**: Record and manage physical activities, sleep patterns, and blood test results
- **Health Score Calculation**: Advanced algorithms to calculate overall health scores based on multiple factors
- **Activity Statistics**: Detailed analytics for daily, weekly, and monthly activity patterns
- **FHIR Integration**: External API integration for healthcare data standards
- **Microservices Architecture**: Scalable, maintainable, and team-friendly development approach

## 🗄️ Database Schema

Each service owns its data with separate PostgreSQL databases:

- **User Service**: `users` table (id, username, email, password)
- **Reference Data Service**: `activity_types`, `blood_test_units` tables
- **Health Data Service**: 
  - `physical_activities` (id, user_id, activity_type_id, duration, calories, date, timestamp)
  - `sleep_activities` (id, user_id, hours, quality, date)
  - `blood_tests` (id, user_id, test_name, value, units_id, date)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Application

1. **Clone and navigate to the project**:
   ```bash
   git clone <repository-url>
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

## 📋 API Endpoints

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

## 🔧 Development

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

### Adding New Features

1. **Identify the service** that should own the feature
2. **Add the endpoint** to the appropriate service
3. **Update the API Gateway** to route the new endpoint
4. **Add tests** for the new functionality

### Local Development

For individual service development:
```bash
# Run specific service locally
cd user-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## 📊 Health Score Calculation

The analytics service calculates health scores based on:
- **Physical Activity**: Duration and calories burned
- **Sleep Quality**: Hours of sleep and quality metrics
- **Blood Test Results**: Medical test values and trends

Scores are normalized to 0-100 scale with personalized recommendations.

## 🔍 Monitoring

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

## 🛠️ Production Considerations

- **Authentication/Authorization**: Implement JWT or OAuth2
- **Service Mesh**: Use Istio or Linkerd for advanced routing
- **Monitoring**: Add Prometheus and Grafana
- **Caching**: Implement Redis for frequently accessed data
- **Message Queue**: Use RabbitMQ or Kafka for async communication
- **Secrets Management**: Use Docker Secrets or external vault

## 🏥 FHIR Integration

The integration service connects to external FHIR servers:
- **Patient Resources**: Fetch patient information
- **Observation Resources**: Health score output in FHIR format
- **Error Handling**: Graceful degradation when external services are unavailable

## 📈 Benefits of Microservices

- **Scalability**: Scale individual services based on demand
- **Team Development**: Different teams can work on different services
- **Technology Flexibility**: Each service can use different technologies
- **Fault Isolation**: Issues in one service don't affect others
- **Deployment Independence**: Deploy services independently

## 🚨 Troubleshooting

### Common Issues

1. **Service not starting**: Check Docker logs
   ```bash
   docker-compose logs [service-name]
   ```

2. **Database connection issues**: Ensure PostgreSQL containers are running
   ```bash
   docker-compose ps
   ```

3. **Service communication errors**: Verify environment variables in docker-compose.yml

### Reset Everything
```bash
docker-compose down -v
docker-compose up -d
```

## 📝 License

This project is licensed under the MIT License.
