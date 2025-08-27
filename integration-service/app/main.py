from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FHIR Integration Service",
    description="Robust FHIR integration service for healthcare data exchange",
    version="2.0.0"
)

# FHIR server configuration
FHIR_SERVER_URL = os.getenv("FHIR_SERVER_URL", "https://hapi.fhir.org/baseR4")
REQUEST_TIMEOUT = int(os.getenv("FHIR_REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("FHIR_MAX_RETRIES", "3"))


class FHIRPatientResponse(BaseModel):
    patient_id: str = Field(..., description="FHIR Patient ID")
    name: str = Field(..., description="Patient full name")
    birth_date: str = Field(..., description="Patient birth date")
    gender: str = Field(..., description="Patient gender")
    address: str = Field(..., description="Patient address")
    contact: str = Field(..., description="Patient contact information")
    resource_type: str = Field(default="Patient", description="FHIR resource type")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    identifiers: Optional[List[Dict[str, str]]] = Field(None, description="Patient identifiers")


class FHIRServerStatus(BaseModel):
    status: str = Field(..., description="Connection status")
    fhir_server_url: str = Field(..., description="FHIR server URL")
    response_status: Optional[int] = Field(None, description="HTTP response status")
    error: Optional[str] = Field(None, description="Error message if any")
    last_check: str = Field(..., description="Last check timestamp")


async def make_fhir_request(client: httpx.AsyncClient, endpoint: str, timeout: int = REQUEST_TIMEOUT) -> Dict[str, Any]:
    """Make a robust FHIR request with retry logic and proper error handling"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Making FHIR request to {endpoint} (attempt {attempt + 1}/{MAX_RETRIES})")
            response = await client.get(endpoint, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
            if attempt == MAX_RETRIES - 1:
                raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt + 1}: {e.response.status_code}")
            if e.response.status_code in [404, 400, 401, 403]:
                raise
            if attempt == MAX_RETRIES - 1:
                raise
        except httpx.RequestError as e:
            logger.error(f"Request error on attempt {attempt + 1}: {e}")
            if attempt == MAX_RETRIES - 1:
                raise
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == MAX_RETRIES - 1:
                raise
    
    raise httpx.RequestError("Max retries exceeded")


def parse_fhir_patient(fhir_data: Dict[str, Any], patient_id: str) -> FHIRPatientResponse:
    """Parse FHIR Patient resource into standardized response"""
    try:
        # Extract name
        name = "Unknown"
        if fhir_data.get('name') and len(fhir_data['name']) > 0:
            name_obj = fhir_data['name'][0]
            given_names = name_obj.get('given', [])
            family_name = name_obj.get('family', '')
            if given_names and family_name:
                name = f"{' '.join(given_names)} {family_name}"
            elif given_names:
                name = ' '.join(given_names)
            elif family_name:
                name = family_name

        # Extract birth date
        birth_date = fhir_data.get('birthDate', 'Unknown')

        # Extract gender
        gender = fhir_data.get('gender', 'Unknown')

        # Extract address
        address = "Unknown"
        if fhir_data.get('address') and len(fhir_data['address']) > 0:
            addr_obj = fhir_data['address'][0]
            line = addr_obj.get('line', [''])[0] if addr_obj.get('line') else ''
            city = addr_obj.get('city', '')
            state = addr_obj.get('state', '')
            postal_code = addr_obj.get('postalCode', '')
            address_parts = [part for part in [line, city, state, postal_code] if part]
            address = ', '.join(address_parts) if address_parts else "Unknown"

        # Extract contact information
        contact = "Unknown"
        if fhir_data.get('telecom') and len(fhir_data['telecom']) > 0:
            for telecom in fhir_data['telecom']:
                if telecom.get('system') in ['phone', 'email']:
                    contact = telecom.get('value', 'Unknown')
                    break

        # Extract identifiers
        identifiers = []
        if fhir_data.get('identifier'):
            for identifier in fhir_data['identifier']:
                identifiers.append({
                    "system": identifier.get('system', ''),
                    "value": identifier.get('value', '')
                })

        return FHIRPatientResponse(
            patient_id=patient_id,
            name=name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            contact=contact,
            last_updated=fhir_data.get('meta', {}).get('lastUpdated'),
            identifiers=identifiers if identifiers else None
        )
    except Exception as e:
        logger.error(f"Error parsing FHIR patient data: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing FHIR patient data: {str(e)}")


@app.get("/fhir_patient/{patient_id}", response_model=FHIRPatientResponse)
async def get_fhir_patient(patient_id: str):
    """Retrieve patient information from FHIR server with robust error handling"""
    if not patient_id or patient_id.strip() == "":
        raise HTTPException(status_code=400, detail="Patient ID is required")
    
    patient_id = patient_id.strip()
    
    try:
        async with httpx.AsyncClient() as client:
            endpoint = f"{FHIR_SERVER_URL}/Patient/{patient_id}"
            fhir_data = await make_fhir_request(client, endpoint)
            
            return parse_fhir_patient(fhir_data, patient_id)
                
    except httpx.TimeoutException:
        logger.error(f"Timeout while fetching patient {patient_id}")
        raise HTTPException(status_code=504, detail="FHIR server timeout - please try again later")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"Patient {patient_id} not found in FHIR server")
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found in FHIR server")
        else:
            logger.error(f"FHIR server error for patient {patient_id}: {e.response.status_code}")
            raise HTTPException(status_code=e.response.status_code, detail=f"FHIR server error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Connection error while fetching patient {patient_id}: {e}")
        raise HTTPException(status_code=503, detail=f"FHIR server connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving patient data: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint with FHIR server connectivity test"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{FHIR_SERVER_URL}/metadata", timeout=5.0)
            fhir_status = "connected" if resp.status_code == 200 else "unhealthy"
    except Exception:
        fhir_status = "disconnected"
    
    return {
        "status": "healthy",
        "service": "integration-service",
        "fhir_server_status": fhir_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/fhir_server_status", response_model=FHIRServerStatus)
async def check_fhir_server_status():
    """Check FHIR server connectivity and status"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{FHIR_SERVER_URL}/metadata", timeout=10.0)
            
            if resp.status_code == 200:
                metadata = resp.json()
                return FHIRServerStatus(
                    status="connected",
                    fhir_server_url=FHIR_SERVER_URL,
                    response_status=resp.status_code,
                    last_check=datetime.utcnow().isoformat()
                )
            else:
                return FHIRServerStatus(
                    status="unhealthy",
                    fhir_server_url=FHIR_SERVER_URL,
                    response_status=resp.status_code,
                    error=f"HTTP {resp.status_code}: {resp.text}",
                    last_check=datetime.utcnow().isoformat()
                )
    except httpx.TimeoutException as e:
        logger.warning(f"FHIR server timeout: {e}")
        return FHIRServerStatus(
            status="timeout",
            fhir_server_url=FHIR_SERVER_URL,
            error=f"Connection timeout: {str(e)}",
            last_check=datetime.utcnow().isoformat()
        )
    except httpx.RequestError as e:
        logger.error(f"FHIR server connection error: {e}")
        return FHIRServerStatus(
            status="disconnected",
            fhir_server_url=FHIR_SERVER_URL,
            error=f"Connection error: {str(e)}",
            last_check=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Unexpected error checking FHIR server: {e}")
        return FHIRServerStatus(
            status="error",
            fhir_server_url=FHIR_SERVER_URL,
            error=f"Unexpected error: {str(e)}",
            last_check=datetime.utcnow().isoformat()
        )
