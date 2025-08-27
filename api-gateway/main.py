from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
REF_DATA_SERVICE_URL = os.getenv("REF_DATA_SERVICE_URL", "http://localhost:8002")
HEALTH_DATA_SERVICE_URL = os.getenv("HEALTH_DATA_SERVICE_URL", "http://localhost:8003")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8004")
INTEGRATION_SERVICE_URL = os.getenv("INTEGRATION_SERVICE_URL", "http://localhost:8005")


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_users(path: str, request: Request):
    return await _proxy(request, f"{USER_SERVICE_URL}/users/{path}")


@app.api_route("/activity_types/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_activity_types(path: str, request: Request):
    return await _proxy(request, f"{REF_DATA_SERVICE_URL}/activity_types/{path}")


@app.api_route("/blood_test_units/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_units(path: str, request: Request):
    return await _proxy(request, f"{REF_DATA_SERVICE_URL}/blood_test_units/{path}")


@app.api_route("/physical_activities/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_physical(path: str, request: Request):
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/physical_activities/{path}")


@app.api_route("/users/{user_id}/physical_activities/{path:path}", methods=["GET", "POST"])
async def proxy_user_physical(user_id: int, path: str, request: Request):
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/{path}")


@app.api_route("/sleep_activities/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_sleep(path: str, request: Request):
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/sleep_activities/{path}")


@app.api_route("/users/{user_id}/sleep_activities/{path:path}", methods=["GET", "POST"])
async def proxy_user_sleep(user_id: int, path: str, request: Request):
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/sleep_activities/{path}")


@app.api_route("/blood_tests/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_blood(path: str, request: Request):
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/blood_tests/{path}")


@app.api_route("/users/{user_id}/blood_tests/{path:path}", methods=["GET", "POST"])
async def proxy_user_blood(user_id: int, path: str, request: Request):
    return await _proxy(request, f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/blood_tests/{path}")


@app.get("/users/{user_id}/get_health_score")
async def proxy_health_score(user_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/users/{user_id}/get_health_score", params=dict(request.query_params))
        return resp.json()


@app.api_route("/users/{user_id}/physical_activities/stats/{period}", methods=["GET"])
async def proxy_stats(user_id: int, period: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/users/{user_id}/physical_activities/stats/{period}", params=dict(request.query_params))
        return resp.json()


@app.get("/fhir_patient/{patient_id}")
async def proxy_fhir(patient_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{INTEGRATION_SERVICE_URL}/fhir_patient/{patient_id}")
        return resp.json()


async def _proxy(request: Request, url: str):
    method = request.method
    headers = dict(request.headers)
    data = await request.body()
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, content=data, params=dict(request.query_params))
        return resp.json()


