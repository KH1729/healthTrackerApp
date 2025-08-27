from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/health_tracker_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    physical_activities = relationship("PhysicalActivity", back_populates="owner")
    sleep_activities = relationship("SleepActivity", back_populates="owner")
    blood_tests = relationship("BloodTest", back_populates="owner")


class PhysicalActivity(Base):
    __tablename__ = "physical_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"))
    duration_minutes = Column(Integer)
    calories_burned = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="physical_activities")
    activity_type = relationship("ActivityType", back_populates="physical_activities")

class ActivityType(Base):
    __tablename__ = "activity_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    physical_activities = relationship("PhysicalActivity", back_populates="activity_type")


class SleepActivity(Base):
    __tablename__ = "sleep_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sleep_duration_hours = Column(Float)
    sleep_quality = Column(Integer)  # e.g., 1-5 scale
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="sleep_activities")


class BloodTest(Base):
    __tablename__ = "blood_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    test_name = Column(String)
    test_result = Column(Float)
    units_id = Column(Integer, ForeignKey("blood_test_units.id"))
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="blood_tests")
    units = relationship("BloodTestUnits", back_populates="blood_tests")

class BloodTestUnits(Base):
    __tablename__ = "blood_test_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    blood_tests = relationship("BloodTest", back_populates="units")


