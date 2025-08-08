from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wallet_address: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wallet_address: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    wallet_address: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Submissions
class SubmissionOut(BaseModel):
    id: int
    user_id: int
    photo_path: str
    greenery_pct: Optional[float] = None
    carbon_value: Optional[float] = None

    class Config:
        from_attributes = True

class SubmissionList(BaseModel):
    submissions: List[SubmissionOut]

# Credits
class CreditOut(BaseModel):
    id: int
    user_id: int
    tonnes_co2: float
    token_id: Optional[str] = None

    class Config:
        from_attributes = True
