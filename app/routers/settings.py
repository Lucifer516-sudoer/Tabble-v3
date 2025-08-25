from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import shutil
from datetime import datetime, timezone

from ..database import (
    Settings, Hotel,
    get_session_db, set_session_hotel_context,
    get_session_hotel_id, authenticate_hotel_session
)
from ..models.settings import Settings as SettingsModel
from ..middleware import get_session_id

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)

# --- Pydantic Models for this router ---

class HotelLoginRequest(BaseModel):
    hotel_name: str
    password: str

class HotelLoginResponse(BaseModel):
    success: bool
    message: str

class HotelInfo(BaseModel):
    hotel_name: str

class HotelListResponse(BaseModel):
    hotels: List[HotelInfo]


# --- Helper Functions ---

# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    # Ensure hotel_id is set for this session before proceeding
    hotel_id = get_session_hotel_id(session_id)
    if not hotel_id:
        raise HTTPException(status_code=401, detail="Hotel context not set. Please log in to a hotel first.")
    return next(get_session_db(session_id, hotel_id))


# --- Endpoints ---

# Get available hotels from the database
@router.get("/hotels", response_model=HotelListResponse)
def get_hotels_from_db(db: Session = Depends(lambda: next(get_session_db(str(os.urandom(24)))))):
    """
    Get a list of all available hotels from the database.
    This endpoint creates a temporary session to query the hotels table.
    """
    try:
        hotels = db.query(Hotel).all()
        hotel_names = [{"hotel_name": hotel.hotel_name} for hotel in hotels]
        return {"hotels": hotel_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading hotel configuration: {str(e)}")

# Get current hotel info
@router.get("/current-hotel")
def get_current_hotel(request: Request, db: Session = Depends(get_session_database)):
    session_id = get_session_id(request)
    hotel_id = get_session_hotel_id(session_id)
    if hotel_id:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if hotel:
            return {"hotel_name": hotel.hotel_name, "hotel_id": hotel.id}
    return {"hotel_name": None, "hotel_id": None}


# Log in to a hotel
@router.post("/hotel-login", response_model=HotelLoginResponse)
def login_to_hotel(request_data: HotelLoginRequest, request: Request):
    """
    Authenticates and sets the hotel context for the current session.
    """
    try:
        session_id = get_session_id(request)
        hotel_id = authenticate_hotel_session(request_data.hotel_name, request_data.password)

        if hotel_id:
            success = set_session_hotel_context(session_id, hotel_id)
            if success:
                return {
                    "success": True,
                    "message": f"Successfully logged into hotel: {request_data.hotel_name}"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to set hotel context")
        else:
            raise HTTPException(status_code=401, detail="Invalid hotel credentials")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging into hotel: {str(e)}")


# Get hotel settings
@router.get("/", response_model=SettingsModel)
def get_settings(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_session_hotel_id(get_session_id(request))
    settings = db.query(Settings).filter(Settings.hotel_id == hotel_id).first()

    if not settings:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        settings = Settings(
            hotel_id=hotel_id,
            hotel_name=hotel.hotel_name,
            address="123 Main Street, City",
            contact_number="+1 123-456-7890",
            email="info@tabblehotel.com",
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


# Update hotel settings
@router.put("/", response_model=SettingsModel)
async def update_settings(
    request: Request,
    hotel_name: str = Form(...),
    address: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    tax_id: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_session_database)
):
    hotel_id = get_session_hotel_id(get_session_id(request))
    settings = db.query(Settings).filter(Settings.hotel_id == hotel_id).first()

    if not settings:
        settings = Settings(hotel_id=hotel_id)
        db.add(settings)

    settings.hotel_name = hotel_name
    settings.address = address
    settings.contact_number = contact_number
    settings.email = email
    settings.tax_id = tax_id

    if logo:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        hotel_name_for_path = hotel.hotel_name if hotel else f"hotel_{hotel_id}"
        hotel_logo_dir = f"app/static/images/logo/{hotel_name_for_path}"
        os.makedirs(hotel_logo_dir, exist_ok=True)
        logo_path = f"{hotel_logo_dir}/hotel_logo_{logo.filename}"
        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        settings.logo_path = f"/static/images/logo/{hotel_name_for_path}/hotel_logo_{logo.filename}"

    settings.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(settings)

    return settings
