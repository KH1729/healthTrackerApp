from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from datetime import datetime, date
import httpx
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./healthdata.db")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
REF_DATA_SERVICE_URL = os.getenv("REF_DATA_SERVICE_URL", "http://localhost:8002")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PhysicalActivity(Base):
    __tablename__ = "physical_activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"))
    duration = Column(Float)
    calories = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SleepActivity(Base):
    __tablename__ = "sleep_activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    hours = Column(Float)
    quality = Column(String)
    date = Column(DateTime, default=datetime.utcnow)


class BloodTest(Base):
    __tablename__ = "blood_tests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    test_name = Column(String)
    value = Column(Float)
    units_id = Column(Integer, ForeignKey("blood_test_units.id"))
    date = Column(DateTime, default=datetime.utcnow)


class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class BloodTestUnits(Base):
    __tablename__ = "blood_test_units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class PhysicalActivityBase(BaseModel):
    user_id: int
    activity_type_id: int
    duration: float
    calories: float
    date: datetime


class PhysicalActivityCreate(PhysicalActivityBase):
    pass


class PhysicalActivityOut(PhysicalActivityBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class SleepActivityBase(BaseModel):
    user_id: int
    hours: float
    quality: str
    date: datetime


class SleepActivityCreate(SleepActivityBase):
    pass


class SleepActivityOut(SleepActivityBase):
    id: int

    class Config:
        from_attributes = True


class BloodTestBase(BaseModel):
    user_id: int
    test_name: str
    value: float
    units_id: int
    date: datetime


class BloodTestCreate(BloodTestBase):
    pass


class BloodTestOut(BloodTestBase):
    id: int

    class Config:
        from_attributes = True


app = FastAPI(
    title="Health Data Service",
    description="Health data management microservice for physical activities, sleep, and blood tests",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def validate_user(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception:
            raise HTTPException(status_code=404, detail="User not found")


async def validate_activity_type(activity_type_id: int):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{REF_DATA_SERVICE_URL}/activity_types/{activity_type_id}")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Activity type not found")
        except Exception:
            raise HTTPException(status_code=404, detail="Activity type not found")


async def validate_blood_test_unit(units_id: int):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{REF_DATA_SERVICE_URL}/blood_test_units/{units_id}")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Blood test unit not found")
        except Exception:
            raise HTTPException(status_code=404, detail="Blood test unit not found")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health_check():
    """Health check endpoint for the health data service"""
    return {
        "status": "healthy",
        "service": "health-data-service",
        "database": "connected" if engine else "disconnected"
    }


@app.post("/physical_activities/", response_model=PhysicalActivityOut)
async def create_physical_activity(activity: PhysicalActivityCreate, db: Session = Depends(get_db)):
    await validate_user(activity.user_id)
    await validate_activity_type(activity.activity_type_id)
    entity = PhysicalActivity(**activity.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@app.get("/physical_activities/", response_model=list[PhysicalActivityOut])
def list_physical_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(PhysicalActivity).offset(skip).limit(limit).all()


@app.get("/users/{user_id}/physical_activities/", response_model=list[PhysicalActivityOut])
def list_user_physical_activities(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).offset(skip).limit(limit).all()


@app.post("/sleep_activities/", response_model=SleepActivityOut)
async def create_sleep_activity(activity: SleepActivityCreate, db: Session = Depends(get_db)):
    await validate_user(activity.user_id)
    entity = SleepActivity(**activity.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@app.get("/sleep_activities/", response_model=list[SleepActivityOut])
def list_sleep_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SleepActivity).offset(skip).limit(limit).all()


@app.get("/users/{user_id}/sleep_activities/", response_model=list[SleepActivityOut])
def list_user_sleep_activities(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SleepActivity).filter(SleepActivity.user_id == user_id).offset(skip).limit(limit).all()


@app.post("/blood_tests/", response_model=BloodTestOut)
async def create_blood_test(test: BloodTestCreate, db: Session = Depends(get_db)):
    await validate_user(test.user_id)
    await validate_blood_test_unit(test.units_id)
    entity = BloodTest(**test.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@app.get("/blood_tests/", response_model=list[BloodTestOut])
def list_blood_tests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(BloodTest).offset(skip).limit(limit).all()


@app.get("/users/{user_id}/blood_tests/", response_model=list[BloodTestOut])
def list_user_blood_tests(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(BloodTest).filter(BloodTest.user_id == user_id).offset(skip).limit(limit).all()
