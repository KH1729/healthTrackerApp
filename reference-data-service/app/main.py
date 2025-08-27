from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./refdata.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class BloodTestUnits(Base):
    __tablename__ = "blood_test_units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class NameBase(BaseModel):
    name: str


class NameOut(NameBase):
    id: int

    class Config:
        from_attributes = True


app = FastAPI(
    title="Reference Data Service",
    description="Reference data management microservice for activity types and blood test units",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health_check():
    """Health check endpoint for the reference data service"""
    return {
        "status": "healthy",
        "service": "reference-data-service",
        "database": "connected" if engine else "disconnected"
    }


@app.post("/activity_types/", response_model=NameOut)
def create_activity_type(payload: NameBase, db: Session = Depends(get_db)):
    entity = ActivityType(name=payload.name)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@app.get("/activity_types/", response_model=list[NameOut])
def list_activity_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ActivityType).offset(skip).limit(limit).all()


@app.get("/activity_types/{id}", response_model=NameOut)
def get_activity_type(id: int, db: Session = Depends(get_db)):
    entity = db.query(ActivityType).filter(ActivityType.id == id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Activity Type not found")
    return entity


@app.post("/blood_test_units/", response_model=NameOut)
def create_blood_test_unit(payload: NameBase, db: Session = Depends(get_db)):
    entity = BloodTestUnits(name=payload.name)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@app.get("/blood_test_units/", response_model=list[NameOut])
def list_blood_test_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(BloodTestUnits).offset(skip).limit(limit).all()


@app.get("/blood_test_units/{id}", response_model=NameOut)
def get_blood_test_unit(id: int, db: Session = Depends(get_db)):
    entity = db.query(BloodTestUnits).filter(BloodTestUnits.id == id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Blood Test Unit not found")
    return entity


