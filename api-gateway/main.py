from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional

# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="Health Tracker API",
    description="""
    # Health Tracker Application API
    
    A health tracking system. This API allows you to:
    
    ##  **Core Features**
    - **User Management**: Create and manage user accounts
    - **Health Data Tracking**: Record physical activities, sleep patterns, and blood test results
    - **Health Analytics**: Calculate health scores and generate statistics
    - **External Integration**: Connect with FHIR healthcare systems
    
    ##  **Getting Started**
    1. Create a user account using the User Management endpoints
    2. Add activity types and blood test units using Reference Data endpoints
    3. Record your health data using Health Data endpoints
    4. View your health analytics and scores using Analytics endpoints
    
    ##  **Health Score Calculation**
    The system calculates health scores based on:
    - Physical activity duration and calories burned
    - Sleep quality and duration
    - Blood test results and trends
    
    Scores are normalized to 0-100 scale with personalized recommendations.
    """,
    version="1.0.0",
    contact={
        "name": "Health Tracker Team",
        "email": "k.hagay+supporthealthtracker@gmail.com",
    },
    openapi_tags=[
        {
            "name": "User Management",
            "description": "Operations for managing user accounts and profiles",
        },
        {
            "name": "Reference Data",
            "description": "Manage activity types and blood test measurement units",
        },
        {
            "name": "Physical Activities",
            "description": "Track and manage physical exercise and activities",
        },
        {
            "name": "Sleep Activities",
            "description": "Record and analyze sleep patterns and quality",
        },
        {
            "name": "Blood Tests",
            "description": "Store and manage blood test results and measurements",
        },
        {
            "name": "Analytics",
            "description": "Health score calculations and activity statistics",
        },
        {
            "name": "External Integration",
            "description": "FHIR API integration for healthcare data exchange",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables for service URLs
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
REF_DATA_SERVICE_URL = os.getenv("REF_DATA_SERVICE_URL", "http://localhost:8002")
HEALTH_DATA_SERVICE_URL = os.getenv("HEALTH_DATA_SERVICE_URL", "http://localhost:8003")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8004")
INTEGRATION_SERVICE_URL = os.getenv("INTEGRATION_SERVICE_URL", "http://localhost:8005")


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Check the health status of the API Gateway and all microservices.
    
    Returns the status of all connected services.
    """
    services = {
        "api_gateway": "healthy",
        "user_service": "checking...",
        "reference_data_service": "checking...",
        "health_data_service": "checking...",
        "analytics_service": "checking...",
        "integration_service": "checking..."
    }
    
    # Check each service
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{USER_SERVICE_URL}/health", timeout=2.0)
            services["user_service"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            services["user_service"] = "unreachable"
            
        try:
            resp = await client.get(f"{REF_DATA_SERVICE_URL}/health", timeout=2.0)
            services["reference_data_service"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            services["reference_data_service"] = "unreachable"
            
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/health", timeout=2.0)
            services["health_data_service"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            services["health_data_service"] = "unreachable"
            
        try:
            resp = await client.get(f"{ANALYTICS_SERVICE_URL}/health", timeout=2.0)
            services["analytics_service"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            services["analytics_service"] = "unreachable"
            
        try:
            resp = await client.get(f"{INTEGRATION_SERVICE_URL}/health", timeout=2.0)
            services["integration_service"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            services["integration_service"] = "unreachable"
    
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": services
    }


@app.get("/test-routing")
async def test_routing():
    """
    Test routing endpoint to verify API Gateway is working.
    """
    print("DEBUG: Test routing endpoint called")
    return {"message": "API Gateway routing is working"}


@app.get("/test-user/{user_id}")
async def test_user_routing(user_id: int):
    """
    Test user-specific routing.
    """
    print(f"DEBUG: Test user routing called for user {user_id}")
    return {"message": f"User routing working for user {user_id}"}


@app.get("/test-simple")
async def test_simple_routing():
    """
    Test simple routing without parameters.
    """
    print("DEBUG: Test simple routing called")
    return {"message": "Simple routing working"}


@app.get("/test-physical/{user_id}")
async def test_physical_routing(user_id: int):
    """
    Test physical activities routing.
    """
    print(f"DEBUG: Test physical routing called for user {user_id}")
    return {"message": f"Physical routing working for user {user_id}"}


@app.get("/test-users/{user_id}")
async def test_users_routing(user_id: int):
    """
    Test users routing pattern.
    """
    print(f"DEBUG: Test users routing called for user {user_id}")
    return {"message": f"Users routing working for user {user_id}"}





# Reference Data Endpoints
@app.api_route("/activity_types/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Reference Data"])
async def proxy_activity_types(path: str, request: Request):
    """
    Activity Type Management
    
    Manage different types of physical activities (e.g., running, swimming, cycling).
    
    - **GET**: Retrieve activity types
    - **POST**: Create new activity type
    - **PUT**: Update activity type
    - **DELETE**: Remove activity type
    """
    return await _proxy(request, f"{REF_DATA_SERVICE_URL}/activity_types/{path}")


@app.api_route("/blood_test_units/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Reference Data"])
async def proxy_units(path: str, request: Request):
    """
    Blood Test Units Management
    
    Manage measurement units for blood test results (e.g., mg/dL, mmol/L, %).
    
    - **GET**: Retrieve blood test units
    - **POST**: Create new blood test unit
    - **PUT**: Update blood test unit
    - **DELETE**: Remove blood test unit
    """
    return await _proxy(request, f"{REF_DATA_SERVICE_URL}/blood_test_units/{path}")


# Physical Activities Endpoints
@app.get("/physical_activities/", tags=["Physical Activities"])
async def proxy_physical_get(request: Request):
    """
    Get all physical activities.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/physical_activities/")


@app.post("/physical_activities/", tags=["Physical Activities"])
async def proxy_physical_post(request: Request):
    """
    Create a new physical activity.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/physical_activities/")


@app.get("/physical_activities/{activity_id}", tags=["Physical Activities"])
async def proxy_physical_get_by_id(activity_id: int, request: Request):
    """
    Get a specific physical activity by ID.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/physical_activities/{activity_id}")


@app.put("/physical_activities/{activity_id}", tags=["Physical Activities"])
async def proxy_physical_put(activity_id: int, request: Request):
    """
    Update a specific physical activity.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/physical_activities/{activity_id}")


@app.delete("/physical_activities/{activity_id}", tags=["Physical Activities"])
async def proxy_physical_delete(activity_id: int, request: Request):
    """
    Delete a specific physical activity.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/physical_activities/{activity_id}")


@app.get("/users/{user_id}/physical_activities/", tags=["Physical Activities"])
async def proxy_user_physical_get(user_id: int, request: Request):
    """
    Get all physical activities for a specific user.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/")


@app.post("/users/{user_id}/physical_activities/", tags=["Physical Activities"])
async def proxy_user_physical_post(user_id: int, request: Request):
    """
    Create a new physical activity for a specific user.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/")


@app.api_route("/users/{user_id}/physical_activities/stats/{period}", methods=["GET"], tags=["Analytics"])
async def proxy_stats(user_id: int, period: str, request: Request):
    """
    Physical Activity Statistics
    
    Get detailed statistics for a user's physical activities over different time periods.
    
    **Parameters:**
    - `user_id`: The ID of the user
    - `period`: Time period for statistics (`last_day`, `last_week`, `last_month`)
    
    **Returns:**
    - Total activities count
    - Total duration and calories
    - Average metrics
    - Detailed activity breakdown
    
    **Available Periods:**
    - `last_day`: Last 24 hours
    - `last_week`: Last 7 days
    - `last_month`: Last 30 days
    """
    if period not in ["last_day", "last_week", "last_month"]:
        raise HTTPException(status_code=400, detail="Invalid period. Use: last_day, last_week, or last_month")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/users/{user_id}/physical_activities/stats/{period}", params=dict(request.query_params))
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to retrieve statistics")
        return resp.json()





# Sleep Activities Endpoints
@app.api_route("/sleep_activities/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Sleep Activities"])
async def proxy_sleep(path: str, request: Request):
    """
    Sleep Activities Management
    
    Record and analyze sleep patterns, duration, and quality.
    
    - **GET**: Retrieve sleep activities
    - **POST**: Create new sleep activity record
    - **PUT**: Update sleep activity record
    - **DELETE**: Remove sleep activity record
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/sleep_activities/{path}")


@app.get("/users/{user_id}/sleep_activities/", tags=["Sleep Activities"])
async def proxy_user_sleep_get(user_id: int, request: Request):
    """
    Get all sleep activities for a specific user.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/sleep_activities/")


@app.post("/users/{user_id}/sleep_activities/", tags=["Sleep Activities"])
async def proxy_user_sleep_post(user_id: int, request: Request):
    """
    Create a new sleep activity for a specific user.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/sleep_activities/")





# Blood Tests Endpoints
@app.api_route("/blood_tests/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Blood Tests"])
async def proxy_blood(path: str, request: Request):
    """
    Blood Tests Management
    
    Store and manage blood test results with values and measurement units.
    
    - **GET**: Retrieve blood tests
    - **POST**: Create new blood test record
    - **PUT**: Update blood test record
    - **DELETE**: Remove blood test record
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/blood_tests/{path}")


@app.get("/users/{user_id}/blood_tests/", tags=["Blood Tests"])
async def proxy_user_blood_get(user_id: int, request: Request):
    """
    Get all blood tests for a specific user.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/blood_tests/")


@app.post("/users/{user_id}/blood_tests/", tags=["Blood Tests"])
async def proxy_user_blood_post(user_id: int, request: Request):
    """
    Create a new blood test for a specific user.
    """
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/blood_tests/")





# Analytics Endpoints
@app.get("/users/{user_id}/get_health_score", tags=["Analytics"])
async def proxy_health_score(user_id: int, days: Optional[int] = 30, request: Request = None):
    """
    Calculate Health Score
    
    Calculate a comprehensive health score for a user based on their recent health data.
    
    **Parameters:**
    - `user_id`: The ID of the user
    - `days`: Number of days to analyze (default: 30)
    
    **Returns:**
    - Overall health score (0-100)
    - Individual component scores (physical activity, sleep, blood tests)
    - Personalized recommendations
    
    **Score Components:**
    - Physical Activity: Based on duration and calories burned
    - Sleep Quality: Based on hours and quality metrics
    - Blood Tests: Based on medical reference ranges
    """
    async with httpx.AsyncClient() as client:
        params = dict(request.query_params) if request else {}
        if days:
            params["days"] = days
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/users/{user_id}/get_health_score", params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to calculate health score")
        return resp.json()


# External Integration Endpoints
@app.get("/fhir_patient/{patient_id}", tags=["External Integration"])
async def proxy_fhir(patient_id: str):
    """
    FHIR Patient Data
    
    Retrieve patient information from external FHIR healthcare systems.
    
    **Parameters:**
    - `patient_id`: The FHIR patient identifier
    
    **Returns:**
    - Patient demographic information
    - Contact details
    - Medical record references
    
    **Note:** This endpoint connects to external FHIR servers and may require authentication.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{INTEGRATION_SERVICE_URL}/fhir_patient/{patient_id}", timeout=10.0)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to retrieve FHIR patient data")
            return resp.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="FHIR server timeout")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"FHIR service error: {str(e)}")


# User Management Endpoints (catch-all route - must be last)
@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["User Management"])
async def proxy_users(path: str, request: Request):
    """
    User Management Operations
    
    - **GET**: Retrieve user information
    - **POST**: Create a new user account
    - **PUT**: Update existing user information
    - **DELETE**: Remove a user account
    
    All user-related operations are handled by the User Service.
    """
    return await _proxy(request, f"{USER_SERVICE_URL}/users/{path}")


# Internal proxy function
async def _proxy(request: Request, url: str):
    """
    Internal proxy function to forward requests to appropriate microservices.
    """
    method = request.method
    headers = dict(request.headers)
    data = await request.body()
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(method, url, headers=headers, content=data, params=dict(request.query_params), timeout=30.0)
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=f"Service error: {resp.text}")
            return resp.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


