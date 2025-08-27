from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class PhysicalActivityBase(BaseModel):
    activity_type_id: int
    duration_minutes: int
    calories_burned: int
    date: Optional[datetime] = None

class PhysicalActivityCreate(PhysicalActivityBase):
    pass

class PhysicalActivity(PhysicalActivityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class SleepActivityBase(BaseModel):
    sleep_duration_hours: float
    sleep_quality: int
    date: Optional[datetime] = None

class SleepActivityCreate(SleepActivityBase):
    pass

class SleepActivity(SleepActivityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class BloodTestBase(BaseModel):
    test_name: str
    test_result: float
    units_id: int
    date: Optional[datetime] = None

class BloodTestCreate(BloodTestBase):
    pass

class BloodTest(BloodTestBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ActivityTypeBase(BaseModel):
    name: str

class ActivityTypeCreate(ActivityTypeBase):
    pass

class ActivityType(ActivityTypeBase):
    id: int

    class Config:
        from_attributes = True

class BloodTestUnitsBase(BaseModel):
    name: str

class BloodTestUnitsCreate(BloodTestUnitsBase):
    pass

class BloodTestUnits(BloodTestUnitsBase):
    id: int

    class Config:
        from_attributes = True
