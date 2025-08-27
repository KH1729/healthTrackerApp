from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Simulated FHIR server URL - in production this would be a real FHIR server
FHIR_SERVER_URL = os.getenv("FHIR_SERVER_URL", "https://hapi.fhir.org/baseR4")


class FHIRPatientResponse(BaseModel):
    patient_id: str
    name: str
    birth_date: str
    gender: str
    address: str
    contact: str
    resource_type: str = "Patient"


@app.get("/fhir_patient/{patient_id}", response_model=FHIRPatientResponse)
async def get_fhir_patient(patient_id: str):
    """
    Retrieve patient information from FHIR server
    This is a simplified implementation - in production you'd use a proper FHIR client
    """
    try:
        async with httpx.AsyncClient() as client:
            # In a real implementation, you'd make a proper FHIR request
            # resp = await client.get(f"{FHIR_SERVER_URL}/Patient/{patient_id}")
            
            # For demo purposes, return mock data
            # In production, you'd parse the actual FHIR response
            if patient_id == "example":
                return FHIRPatientResponse(
                    patient_id=patient_id,
                    name="John Doe",
                    birth_date="1990-01-01",
                    gender="male",
                    address="123 Main St, City, State 12345",
                    contact="john.doe@email.com"
                )
            else:
                # Simulate a real FHIR request that might fail
                resp = await client.get(f"{FHIR_SERVER_URL}/Patient/{patient_id}", timeout=10.0)
                if resp.status_code == 404:
                    raise HTTPException(status_code=404, detail="Patient not found in FHIR server")
                elif resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail="FHIR server error")
                
                # Parse FHIR response (simplified)
                fhir_data = resp.json()
                return FHIRPatientResponse(
                    patient_id=patient_id,
                    name=f"{fhir_data.get('name', [{}])[0].get('given', ['Unknown'])[0]} {fhir_data.get('name', [{}])[0].get('family', 'Unknown')}",
                    birth_date=fhir_data.get('birthDate', 'Unknown'),
                    gender=fhir_data.get('gender', 'Unknown'),
                    address=f"{fhir_data.get('address', [{}])[0].get('line', ['Unknown'])[0]}, {fhir_data.get('address', [{}])[0].get('city', 'Unknown')}",
                    contact=fhir_data.get('telecom', [{}])[0].get('value', 'Unknown') if fhir_data.get('telecom') else 'Unknown'
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="FHIR server timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"FHIR server connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient data: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint for the integration service"""
    return {"status": "healthy", "service": "integration-service"}


@app.get("/fhir_server_status")
async def check_fhir_server_status():
    """Check if the FHIR server is accessible"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{FHIR_SERVER_URL}/metadata", timeout=5.0)
            return {
                "status": "connected",
                "fhir_server_url": FHIR_SERVER_URL,
                "response_status": resp.status_code
            }
    except Exception as e:
        return {
            "status": "disconnected",
            "fhir_server_url": FHIR_SERVER_URL,
            "error": str(e)
        }
