from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx
import os

HEALTH_DATA_SERVICE_URL = os.getenv("HEALTH_DATA_SERVICE_URL", "http://localhost:8003")

app = FastAPI(
    title="Analytics Service",
    description="Health analytics and statistics microservice for calculating health scores and activity metrics",
    version="1.0.0"
)


class HealthScoreResponse(BaseModel):
    user_id: int
    health_score: float
    physical_activity_score: float
    sleep_score: float
    blood_test_score: float
    recommendations: list[str]


class ActivityStatsResponse(BaseModel):
    user_id: int
    period: str
    total_activities: int
    total_duration: float
    total_calories: float
    average_duration: float
    average_calories: float
    activities: list[dict]


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "analytics-service"
    }


@app.get("/users/{user_id}/get_health_score", response_model=HealthScoreResponse)
async def get_health_score(user_id: int, days: int = 30):
    async with httpx.AsyncClient() as client:
        # Get physical activities
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
            physical_activities = resp.json()
        except Exception:
            physical_activities = []

        # Get sleep activities
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/sleep_activities/")
            sleep_activities = resp.json() if resp.status_code == 200 else []
        except Exception:
            sleep_activities = []

        # Get blood tests
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/blood_tests/")
            blood_tests = resp.json() if resp.status_code == 200 else []
        except Exception:
            blood_tests = []

        # Calculate scores
        physical_score = calculate_physical_activity_score(physical_activities, days)
        sleep_score = calculate_sleep_score(sleep_activities, days)
        blood_score = calculate_blood_test_score(blood_tests, days)

        # Calculate overall health score
        overall_score = (physical_score + sleep_score + blood_score) / 3

        # Generate recommendations
        recommendations = generate_recommendations(physical_score, sleep_score, blood_score)

        return HealthScoreResponse(
            user_id=user_id,
            health_score=overall_score,
            physical_activity_score=physical_score,
            sleep_score=sleep_score,
            blood_test_score=blood_score,
            recommendations=recommendations
        )


@app.get("/users/{user_id}/physical_activities/stats/last_day", response_model=ActivityStatsResponse)
async def get_last_day_activity_stats(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
            activities = resp.json()
        except Exception:
            activities = []

    # Filter for last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    recent_activities = [
        activity for activity in activities
        if datetime.fromisoformat(activity["date"].replace("Z", "+00:00")) >= yesterday
    ]

    if not recent_activities:
        return ActivityStatsResponse(
            user_id=user_id,
            period="last_day",
            total_activities=0,
            total_duration=0,
            total_calories=0,
            average_duration=0,
            average_calories=0,
            activities=[]
        )

    total_duration = sum(activity["duration"] for activity in recent_activities)
    total_calories = sum(activity["calories"] for activity in recent_activities)

    return ActivityStatsResponse(
        user_id=user_id,
        period="last_day",
        total_activities=len(recent_activities),
        total_duration=total_duration,
        total_calories=total_calories,
        average_duration=total_duration / len(recent_activities),
        average_calories=total_calories / len(recent_activities),
        activities=recent_activities
    )


@app.get("/users/{user_id}/physical_activities/stats/last_week", response_model=ActivityStatsResponse)
async def get_last_week_activity_stats(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
            activities = resp.json()
        except Exception:
            activities = []

    # Filter for last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    recent_activities = [
        activity for activity in activities
        if datetime.fromisoformat(activity["date"].replace("Z", "+00:00")) >= week_ago
    ]

    if not recent_activities:
        return ActivityStatsResponse(
            user_id=user_id,
            period="last_week",
            total_activities=0,
            total_duration=0,
            total_calories=0,
            average_duration=0,
            average_calories=0,
            activities=[]
        )

    total_duration = sum(activity["duration"] for activity in recent_activities)
    total_calories = sum(activity["calories"] for activity in recent_activities)

    return ActivityStatsResponse(
        user_id=user_id,
        period="last_week",
        total_activities=len(recent_activities),
        total_duration=total_duration,
        total_calories=total_calories,
        average_duration=total_duration / len(recent_activities),
        average_calories=total_calories / len(recent_activities),
        activities=recent_activities
    )


@app.get("/users/{user_id}/physical_activities/stats/last_month", response_model=ActivityStatsResponse)
async def get_last_month_activity_stats(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{HEALTH_DATA_SERVICE_URL}/users/{user_id}/physical_activities/")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
            activities = resp.json()
        except Exception:
            activities = []

    # Filter for last 30 days
    month_ago = datetime.now() - timedelta(days=30)
    recent_activities = [
        activity for activity in activities
        if datetime.fromisoformat(activity["date"].replace("Z", "+00:00")) >= month_ago
    ]

    if not recent_activities:
        return ActivityStatsResponse(
            user_id=user_id,
            period="last_month",
            total_activities=0,
            total_duration=0,
            total_calories=0,
            average_duration=0,
            average_calories=0,
            activities=[]
        )

    total_duration = sum(activity["duration"] for activity in recent_activities)
    total_calories = sum(activity["calories"] for activity in recent_activities)

    return ActivityStatsResponse(
        user_id=user_id,
        period="last_month",
        total_activities=len(recent_activities),
        total_duration=total_duration,
        total_calories=total_calories,
        average_duration=total_duration / len(recent_activities),
        average_calories=total_calories / len(recent_activities),
        activities=recent_activities
    )


def calculate_physical_activity_score(activities, days):
    if not activities:
        return 0.0
    
    # Filter activities for the specified period
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_activities = [
        activity for activity in activities
        if datetime.fromisoformat(activity["date"].replace("Z", "+00:00")) >= cutoff_date
    ]
    
    if not recent_activities:
        return 0.0
    
    total_duration = sum(activity["duration"] for activity in recent_activities)
    total_calories = sum(activity["calories"] for activity in recent_activities)
    
    # Score based on duration and calories (simplified scoring)
    duration_score = min(total_duration / (days * 30), 1.0)  # 30 minutes per day target
    calories_score = min(total_calories / (days * 200), 1.0)  # 200 calories per day target
    
    return (duration_score + calories_score) / 2 * 100


def calculate_sleep_score(activities, days):
    if not activities:
        return 0.0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_activities = [
        activity for activity in activities
        if datetime.fromisoformat(activity["date"].replace("Z", "+00:00")) >= cutoff_date
    ]
    
    if not recent_activities:
        return 0.0
    
    total_hours = sum(activity["hours"] for activity in recent_activities)
    avg_hours = total_hours / len(recent_activities)
    
    # Score based on 7-9 hours being optimal
    if 7 <= avg_hours <= 9:
        return 100.0
    elif 6 <= avg_hours < 7 or 9 < avg_hours <= 10:
        return 80.0
    elif 5 <= avg_hours < 6 or 10 < avg_hours <= 11:
        return 60.0
    else:
        return 40.0


def calculate_blood_test_score(tests, days):
    if not tests:
        return 0.0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_tests = [
        test for test in tests
        if datetime.fromisoformat(test["date"].replace("Z", "+00:00")) >= cutoff_date
    ]
    
    if not recent_tests:
        return 0.0
    
    # Simplified scoring - assume tests are within normal ranges
    # In a real implementation, you'd check against medical reference ranges
    return 85.0  # Placeholder score


def generate_recommendations(physical_score, sleep_score, blood_score):
    recommendations = []
    
    if physical_score < 70:
        recommendations.append("Increase physical activity to at least 30 minutes per day")
    
    if sleep_score < 70:
        recommendations.append("Aim for 7-9 hours of sleep per night")
    
    if blood_score < 70:
        recommendations.append("Consider consulting with a healthcare provider about your blood test results")
    
    if not recommendations:
        recommendations.append("Keep up the great work! Your health metrics look good.")
    
    return recommendations
