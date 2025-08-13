from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonBase(BaseModel):
    username: str

class PersonCreate(PersonBase):
    password: str
    table_number: int
    phone_number: Optional[str] = None

class PersonLogin(PersonBase):
    password: str
    table_number: int

class PhoneAuthRequest(BaseModel):
    phone_number: str
    table_number: int

class PhoneVerifyRequest(BaseModel):
    phone_number: str
    verification_code: str
    token: str
    table_number: int

class UsernameRequest(BaseModel):
    phone_number: str
    username: str
    table_number: int

class Person(PersonBase):
    id: int
    visit_count: int
    last_visit: datetime
    created_at: datetime
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2
