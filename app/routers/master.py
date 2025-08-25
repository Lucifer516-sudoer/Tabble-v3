from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import database
from ..auth import verify_master_password
from ..models import hotel as hotel_models

router = APIRouter(
    prefix="/master",
    tags=["master"],
    dependencies=[Depends(verify_master_password)],
    responses={404: {"description": "Not found"}},
)

@router.post("/hotels", response_model=hotel_models.Hotel, status_code=201)
def create_hotel(
    hotel: hotel_models.HotelCreate, db: Session = Depends(database.get_db)
):
    """
    Create a new hotel. Requires master password authentication.
    """
    db_hotel = db.query(database.Hotel).filter(database.Hotel.hotel_name == hotel.hotel_name).first()
    if db_hotel:
        raise HTTPException(status_code=400, detail="Hotel with this name already exists")

    new_hotel = database.Hotel(hotel_name=hotel.hotel_name, password=hotel.password)
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel

@router.get("/hotels", response_model=List[hotel_models.Hotel])
def get_all_hotels(db: Session = Depends(database.get_db)):
    """
    Get a list of all hotels. Requires master password authentication.
    """
    hotels = db.query(database.Hotel).all()
    return hotels

@router.put("/hotels/{hotel_id}", response_model=hotel_models.Hotel)
def update_hotel(
    hotel_id: int,
    hotel_update: hotel_models.HotelUpdate,
    db: Session = Depends(database.get_db),
):
    """
    Update a hotel's details. Requires master password authentication.
    """
    db_hotel = db.query(database.Hotel).filter(database.Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    update_data = hotel_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hotel, key, value)

    db.commit()
    db.refresh(db_hotel)
    return db_hotel
