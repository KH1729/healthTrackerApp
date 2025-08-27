from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import httpx

from .database import SessionLocal, engine, Base, User, PhysicalActivity, SleepActivity, BloodTest, ActivityType, BloodTestUnits
from . import schemas

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create database tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Helper function to calculate health score for a user
def calculate_user_health_score(user_id: int, db: Session):
    score = 0

    # Physical Activity Score
    physical_activities = db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).all()
    for activity in physical_activities:
        score += activity.duration_minutes * 0.1  # 0.1 points per minute of activity
        score += activity.calories_burned * 0.05  # 0.05 points per calorie burned

    # Sleep Activity Score
    sleep_activities = db.query(SleepActivity).filter(SleepActivity.user_id == user_id).all()
    for sleep in sleep_activities:
        if 7 <= sleep.sleep_duration_hours <= 9:
            score += 10 # Optimal sleep
        elif 6 <= sleep.sleep_duration_hours < 7 or 9 < sleep.sleep_duration_hours <= 10:
            score += 5 # Near optimal sleep
        else:
            score += 2 # Suboptimal sleep
        score += sleep.sleep_quality * 2 # 2 points per sleep quality unit (e.g., 1-5 scale)

    # Blood Test Score (Example: Glucose)
    blood_tests = db.query(BloodTest).filter(BloodTest.user_id == user_id, BloodTest.test_name == "glucose").all()
    for test in blood_tests:
        if 70 <= test.test_result <= 100: # Normal glucose levels
            score += 15
        elif 50 <= test.test_result < 70 or 100 < test.test_result <= 130: # Borderline
            score += 5
        else:
            score += 0 # Unhealthy

    return score

# CRUD for Users
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(username=user.username, email=user.email, password=user.password) # In a real app, hash the password!
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password # In a real app, hash the password!
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user

# CRUD for Activity Types
@app.post("/activity_types/", response_model=schemas.ActivityType)
def create_activity_type(activity_type: schemas.ActivityTypeCreate, db: Session = Depends(get_db)):
    db_activity_type = ActivityType(**activity_type.dict())
    db.add(db_activity_type)
    db.commit()
    db.refresh(db_activity_type)
    return db_activity_type

@app.get("/activity_types/", response_model=List[schemas.ActivityType])
def read_activity_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activity_types = db.query(ActivityType).offset(skip).limit(limit).all()
    return activity_types

@app.get("/activity_types/{activity_type_id}", response_model=schemas.ActivityType)
def read_activity_type(activity_type_id: int, db: Session = Depends(get_db)):
    activity_type = db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    if activity_type is None:
        raise HTTPException(status_code=404, detail="Activity Type not found")
    return activity_type

# CRUD for Blood Test Units
@app.post("/blood_test_units/", response_model=schemas.BloodTestUnits)
def create_blood_test_unit(unit: schemas.BloodTestUnitsCreate, db: Session = Depends(get_db)):
    db_unit = BloodTestUnits(**unit.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@app.get("/blood_test_units/", response_model=List[schemas.BloodTestUnits])
def read_blood_test_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    units = db.query(BloodTestUnits).offset(skip).limit(limit).all()
    return units

@app.get("/blood_test_units/{unit_id}", response_model=schemas.BloodTestUnits)
def read_blood_test_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(BloodTestUnits).filter(BloodTestUnits.id == unit_id).first()
    if unit is None:
        raise HTTPException(status_code=404, detail="Blood Test Unit not found")
    return unit

# CRUD for Physical Activities
@app.post("/users/{user_id}/physical_activities/", response_model=schemas.PhysicalActivity)
def create_physical_activity_for_user(
    user_id: int,
    activity: schemas.PhysicalActivityCreate,
    db: Session = Depends(get_db)
):
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate activity type exists
    activity_type = db.query(ActivityType).filter(ActivityType.id == activity.activity_type_id).first()
    if activity_type is None:
        raise HTTPException(status_code=404, detail="Activity type not found")
    
    db_activity = PhysicalActivity(**activity.dict(), user_id=user_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.get("/users/{user_id}/physical_activities/", response_model=List[schemas.PhysicalActivity])
def read_physical_activities_for_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    activities = db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).offset(skip).limit(limit).all()
    return activities

@app.get("/physical_activities/{activity_id}", response_model=schemas.PhysicalActivity)
def read_physical_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(PhysicalActivity).filter(PhysicalActivity.id == activity_id).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="Physical Activity not found")
    return activity

@app.put("/physical_activities/{activity_id}", response_model=schemas.PhysicalActivity)
def update_physical_activity(
    activity_id: int,
    activity: schemas.PhysicalActivityCreate,
    db: Session = Depends(get_db)
):
    db_activity = db.query(PhysicalActivity).filter(PhysicalActivity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Physical Activity not found")
    for key, value in activity.dict().items():
        setattr(db_activity, key, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.delete("/physical_activities/{activity_id}", response_model=schemas.PhysicalActivity)
def delete_physical_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = db.query(PhysicalActivity).filter(PhysicalActivity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Physical Activity not found")
    db.delete(db_activity)
    db.commit()
    return db_activity

# CRUD for Sleep Activities
@app.post("/users/{user_id}/sleep_activities/", response_model=schemas.SleepActivity)
def create_sleep_activity_for_user(
    user_id: int,
    sleep: schemas.SleepActivityCreate,
    db: Session = Depends(get_db)
):
    db_sleep = SleepActivity(**sleep.dict(), user_id=user_id)
    db.add(db_sleep)
    db.commit()
    db.refresh(db_sleep)
    return db_sleep

@app.get("/users/{user_id}/sleep_activities/", response_model=List[schemas.SleepActivity])
def read_sleep_activities_for_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    sleep_activities = db.query(SleepActivity).filter(SleepActivity.user_id == user_id).offset(skip).limit(limit).all()
    return sleep_activities

@app.get("/sleep_activities/{sleep_id}", response_model=schemas.SleepActivity)
def read_sleep_activity(sleep_id: int, db: Session = Depends(get_db)):
    sleep = db.query(SleepActivity).filter(SleepActivity.id == sleep_id).first()
    if sleep is None:
        raise HTTPException(status_code=404, detail="Sleep Activity not found")
    return sleep

@app.put("/sleep_activities/{sleep_id}", response_model=schemas.SleepActivity)
def update_sleep_activity(
    sleep_id: int,
    sleep: schemas.SleepActivityCreate,
    db: Session = Depends(get_db)
):
    db_sleep = db.query(SleepActivity).filter(SleepActivity.id == sleep_id).first()
    if db_sleep is None:
        raise HTTPException(status_code=404, detail="Sleep Activity not found")
    for key, value in sleep.dict().items():
        setattr(db_sleep, key, value)
    db.commit()
    db.refresh(db_sleep)
    return db_sleep

@app.delete("/sleep_activities/{sleep_id}", response_model=schemas.SleepActivity)
def delete_sleep_activity(sleep_id: int, db: Session = Depends(get_db)):
    db_sleep = db.query(SleepActivity).filter(SleepActivity.id == sleep_id).first()
    if db_sleep is None:
        raise HTTPException(status_code=404, detail="Sleep Activity not found")
    db.delete(db_sleep)
    db.commit()
    return db_sleep

# CRUD for Blood Tests
@app.post("/users/{user_id}/blood_tests/", response_model=schemas.BloodTest)
def create_blood_test_for_user(
    user_id: int,
    blood_test: schemas.BloodTestCreate,
    db: Session = Depends(get_db)
):
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate units exist
    unit = db.query(BloodTestUnits).filter(BloodTestUnits.id == blood_test.units_id).first()
    if unit is None:
        raise HTTPException(status_code=404, detail="Blood test unit not found")
    
    db_blood_test = BloodTest(**blood_test.dict(), user_id=user_id)
    db.add(db_blood_test)
    db.commit()
    db.refresh(db_blood_test)
    return db_blood_test

@app.get("/users/{user_id}/blood_tests/", response_model=List[schemas.BloodTest])
def read_blood_tests_for_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    blood_tests = db.query(BloodTest).filter(BloodTest.user_id == user_id).offset(skip).limit(limit).all()
    return blood_tests

@app.get("/blood_tests/{blood_test_id}", response_model=schemas.BloodTest)
def read_blood_test(blood_test_id: int, db: Session = Depends(get_db)):
    blood_test = db.query(BloodTest).filter(BloodTest.id == blood_test_id).first()
    if blood_test is None:
        raise HTTPException(status_code=404, detail="Blood Test not found")
    return blood_test

@app.put("/blood_tests/{blood_test_id}", response_model=schemas.BloodTest)
def update_blood_test(
    blood_test_id: int,
    blood_test: schemas.BloodTestCreate,
    db: Session = Depends(get_db)
):
    db_blood_test = db.query(BloodTest).filter(BloodTest.id == blood_test_id).first()
    if db_blood_test is None:
        raise HTTPException(status_code=404, detail="Blood Test not found")
    for key, value in blood_test.dict().items():
        setattr(db_blood_test, key, value)
    db.commit()
    db.refresh(db_blood_test)
    return db_blood_test

@app.delete("/blood_tests/{blood_test_id}", response_model=schemas.BloodTest)
def delete_blood_test(blood_test_id: int, db: Session = Depends(get_db)):
    db_blood_test = db.query(BloodTest).filter(BloodTest.id == blood_test_id).first()
    if db_blood_test is None:
        raise HTTPException(status_code=404, detail="Blood Test not found")
    db.delete(db_blood_test)
    db.commit()
    return db_blood_test

@app.get("/users/{user_id}/get_health_score")
def get_health_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_score = calculate_user_health_score(user_id, db)

    # Calculate average score of all users for comparison
    all_users = db.query(User).all()
    total_score = 0
    for u in all_users:
        total_score += calculate_user_health_score(u.id, db)
    
    average_score = total_score / len(all_users) if len(all_users) > 0 else 0

    # Compare user's score to average
    score_comparison = ""
    if user_score > average_score:
        score_comparison = "above average"
    elif user_score < average_score:
        score_comparison = "below average"
    else:
        score_comparison = "average"

    # FHIR-compliant Observation resource
    fhir_observation = {
        "resourceType": "Observation",
        "id": f"health-score-{user_id}",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "87600-3",
                    "display": "Health Score"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{user_id}",
            "display": user.username
        },
        "valueQuantity": {
            "value": round(user_score, 2),
            "unit": "points",
            "system": "http://unitsofmeasure.org",
            "code": "health-points"
        },
        "interpretation": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        "code": "N",
                        "display": "Normal (health score is " + score_comparison + ")"
                    }
                ]
            }
        ],
        "effectiveDateTime": datetime.utcnow().isoformat()
    }

    return fhir_observation

# Physical Activity Statistics Endpoints
@app.get("/users/{user_id}/physical_activities/stats/last_day")
def get_last_day_activity_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate time 24 hours ago
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    # Query activities from last 24 hours
    activities = db.query(PhysicalActivity).filter(
        PhysicalActivity.user_id == user_id,
        PhysicalActivity.date >= yesterday
    ).all()
    
    if not activities:
        return {
            "user_id": user_id,
            "period": "last_24_hours",
            "total_activities": 0,
            "total_duration_minutes": 0,
            "total_calories_burned": 0,
            "average_duration_minutes": 0,
            "average_calories_burned": 0,
            "activities": []
        }
    
    total_duration = sum(activity.duration_minutes for activity in activities)
    total_calories = sum(activity.calories_burned for activity in activities)
    
    return {
        "user_id": user_id,
        "period": "last_24_hours",
        "total_activities": len(activities),
        "total_duration_minutes": total_duration,
        "total_calories_burned": total_calories,
        "average_duration_minutes": round(total_duration / len(activities), 2),
        "average_calories_burned": round(total_calories / len(activities), 2),
        "activities": [
            {
                "id": activity.id,
                "activity_type_id": activity.activity_type_id,
                "activity_type_name": activity.activity_type.name if activity.activity_type else None,
                "duration_minutes": activity.duration_minutes,
                "calories_burned": activity.calories_burned,
                "date": activity.date.isoformat()
            }
            for activity in activities
        ]
    }

@app.get("/users/{user_id}/physical_activities/stats/last_week")
def get_last_week_activity_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate time 7 days ago
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Query activities from last 7 days
    activities = db.query(PhysicalActivity).filter(
        PhysicalActivity.user_id == user_id,
        PhysicalActivity.date >= week_ago
    ).all()
    
    if not activities:
        return {
            "user_id": user_id,
            "period": "last_7_days",
            "total_activities": 0,
            "total_duration_minutes": 0,
            "total_calories_burned": 0,
            "average_duration_minutes_per_activity": 0,
            "average_calories_burned_per_activity": 0,
            "average_duration_minutes_per_day": 0,
            "average_calories_burned_per_day": 0,
            "activities_per_day": 0
        }
    
    total_duration = sum(activity.duration_minutes for activity in activities)
    total_calories = sum(activity.calories_burned for activity in activities)
    
    # Calculate daily averages
    days_in_period = 7
    avg_duration_per_day = total_duration / days_in_period
    avg_calories_per_day = total_calories / days_in_period
    avg_activities_per_day = len(activities) / days_in_period
    
    return {
        "user_id": user_id,
        "period": "last_7_days",
        "total_activities": len(activities),
        "total_duration_minutes": total_duration,
        "total_calories_burned": total_calories,
        "average_duration_minutes_per_activity": round(total_duration / len(activities), 2),
        "average_calories_burned_per_activity": round(total_calories / len(activities), 2),
        "average_duration_minutes_per_day": round(avg_duration_per_day, 2),
        "average_calories_burned_per_day": round(avg_calories_per_day, 2),
        "activities_per_day": round(avg_activities_per_day, 2)
    }

@app.get("/users/{user_id}/physical_activities/stats/last_month")
def get_last_month_activity_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate time 30 days ago
    from datetime import timedelta
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query activities from last 30 days
    activities = db.query(PhysicalActivity).filter(
        PhysicalActivity.user_id == user_id,
        PhysicalActivity.date >= month_ago
    ).all()
    
    if not activities:
        return {
            "user_id": user_id,
            "period": "last_30_days",
            "total_activities": 0,
            "total_duration_minutes": 0,
            "total_calories_burned": 0,
            "average_duration_minutes_per_activity": 0,
            "average_calories_burned_per_activity": 0,
            "average_duration_minutes_per_day": 0,
            "average_calories_burned_per_day": 0,
            "activities_per_day": 0
        }
    
    total_duration = sum(activity.duration_minutes for activity in activities)
    total_calories = sum(activity.calories_burned for activity in activities)
    
    # Calculate daily averages
    days_in_period = 30
    avg_duration_per_day = total_duration / days_in_period
    avg_calories_per_day = total_calories / days_in_period
    avg_activities_per_day = len(activities) / days_in_period
    
    return {
        "user_id": user_id,
        "period": "last_30_days",
        "total_activities": len(activities),
        "total_duration_minutes": total_duration,
        "total_calories_burned": total_calories,
        "average_duration_minutes_per_activity": round(total_duration / len(activities), 2),
        "average_calories_burned_per_activity": round(total_calories / len(activities), 2),
        "average_duration_minutes_per_day": round(avg_duration_per_day, 2),
        "average_calories_burned_per_day": round(avg_calories_per_day, 2),
        "activities_per_day": round(avg_activities_per_day, 2)
    }

# External FHIR API Integration
@app.get("/fhir_patient/{patient_id}")
async def get_fhir_patient(patient_id: str):
    fhir_api_url = "http://hapi.fhir.org/baseR4"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{fhir_api_url}/Patient/{patient_id}")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching FHIR patient: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error fetching FHIR patient: {e}")
