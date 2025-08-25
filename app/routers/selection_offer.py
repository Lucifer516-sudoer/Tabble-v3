from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import SelectionOffer as SelectionOfferModel, get_session_db, get_hotel_id_from_request
from ..models.selection_offer import (
    SelectionOffer,
    SelectionOfferCreate,
    SelectionOfferUpdate,
)
from ..middleware import get_session_id

router = APIRouter(
    prefix="/selection-offers",
    tags=["selection-offers"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    return next(get_session_db(session_id))


# Get all selection offers
@router.get("/", response_model=List[SelectionOffer])
def get_all_selection_offers(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    return db.query(SelectionOfferModel).filter(SelectionOfferModel.hotel_id == hotel_id).order_by(SelectionOfferModel.min_amount).all()


# Get active selection offers
@router.get("/active", response_model=List[SelectionOffer])
def get_active_selection_offers(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    return (
        db.query(SelectionOfferModel)
        .filter(
            SelectionOfferModel.hotel_id == hotel_id,
            SelectionOfferModel.is_active == True
        )
        .order_by(SelectionOfferModel.min_amount)
        .all()
    )


# Get selection offer by ID
@router.get("/{offer_id}", response_model=SelectionOffer)
def get_selection_offer(offer_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    db_offer = (
        db.query(SelectionOfferModel).filter(
            SelectionOfferModel.hotel_id == hotel_id,
            SelectionOfferModel.id == offer_id
        ).first()
    )
    if not db_offer:
        raise HTTPException(status_code=404, detail="Selection offer not found")
    return db_offer


# Create new selection offer
@router.post("/", response_model=SelectionOffer)
def create_selection_offer(offer: SelectionOfferCreate, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Check if an offer with this min_amount already exists for this hotel
    existing_offer = (
        db.query(SelectionOfferModel)
        .filter(
            SelectionOfferModel.hotel_id == hotel_id,
            SelectionOfferModel.min_amount == offer.min_amount
        )
        .first()
    )
    if existing_offer:
        raise HTTPException(
            status_code=400,
            detail=f"Selection offer with minimum amount {offer.min_amount} already exists",
        )

    # Create new offer
    db_offer = SelectionOfferModel(
        hotel_id=hotel_id,
        min_amount=offer.min_amount,
        discount_amount=offer.discount_amount,
        is_active=offer.is_active,
        description=offer.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


# Update selection offer
@router.put("/{offer_id}", response_model=SelectionOffer)
def update_selection_offer(
    offer_id: int, offer_update: SelectionOfferUpdate, request: Request, db: Session = Depends(get_session_database)
):
    hotel_id = get_hotel_id_from_request(request)

    db_offer = (
        db.query(SelectionOfferModel).filter(
            SelectionOfferModel.hotel_id == hotel_id,
            SelectionOfferModel.id == offer_id
        ).first()
    )
    if not db_offer:
        raise HTTPException(status_code=404, detail="Selection offer not found")

    # Check if updating min_amount and if it already exists for this hotel
    if (
        offer_update.min_amount is not None
        and offer_update.min_amount != db_offer.min_amount
    ):
        existing_offer = (
            db.query(SelectionOfferModel)
            .filter(
                SelectionOfferModel.hotel_id == hotel_id,
                SelectionOfferModel.min_amount == offer_update.min_amount,
                SelectionOfferModel.id != offer_id,
            )
            .first()
        )
        if existing_offer:
            raise HTTPException(
                status_code=400,
                detail=f"Selection offer with minimum amount {offer_update.min_amount} already exists",
            )
        db_offer.min_amount = offer_update.min_amount

    # Update other fields if provided
    if offer_update.discount_amount is not None:
        db_offer.discount_amount = offer_update.discount_amount
    if offer_update.is_active is not None:
        db_offer.is_active = offer_update.is_active
    if offer_update.description is not None:
        db_offer.description = offer_update.description

    db_offer.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_offer)
    return db_offer


# Delete selection offer
@router.delete("/{offer_id}")
def delete_selection_offer(offer_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    db_offer = (
        db.query(SelectionOfferModel).filter(
            SelectionOfferModel.hotel_id == hotel_id,
            SelectionOfferModel.id == offer_id
        ).first()
    )
    if not db_offer:
        raise HTTPException(status_code=404, detail="Selection offer not found")

    db.delete(db_offer)
    db.commit()
    return {"message": "Selection offer deleted successfully"}


# Get applicable discount for an order amount
@router.get("/discount/{order_amount}")
def get_discount_for_order_amount(order_amount: float, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Find the highest tier that the order amount qualifies for this hotel
    applicable_offer = (
        db.query(SelectionOfferModel)
        .filter(
            SelectionOfferModel.hotel_id == hotel_id,
            SelectionOfferModel.min_amount <= order_amount,
            SelectionOfferModel.is_active == True,
        )
        .order_by(SelectionOfferModel.min_amount.desc())
        .first()
    )

    if not applicable_offer:
        return {
            "discount_amount": 0,
            "message": "No applicable selection offer discount",
        }

    return {
        "discount_amount": applicable_offer.discount_amount,
        "offer_id": applicable_offer.id,
        "min_amount": applicable_offer.min_amount,
        "message": f"Selection offer discount of ₹{applicable_offer.discount_amount} applied",
    }
