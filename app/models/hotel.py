from pydantic import BaseModel
from typing import Optional

class HotelBase(BaseModel):
    """Base model for Hotel, containing common attributes."""
    hotel_name: str

class HotelCreate(HotelBase):
    """Model for creating a new hotel, requires a password."""
    password: str

class HotelUpdate(BaseModel):
    """Model for updating an existing hotel. All fields are optional."""
    hotel_name: Optional[str] = None
    password: Optional[str] = None

class Hotel(HotelBase):
    """Model for representing a hotel in API responses, includes the ID."""
    id: int

    class Config:
        from_attributes = True
