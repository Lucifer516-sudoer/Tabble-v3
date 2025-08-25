from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import LoyaltyProgram as LoyaltyProgramModel, get_session_db, get_hotel_id_from_request
from ..models.loyalty import LoyaltyProgram, LoyaltyProgramCreate, LoyaltyProgramUpdate
from ..middleware import get_session_id

router = APIRouter(
    prefix="/loyalty",
    tags=["loyalty"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    return next(get_session_db(session_id))


# Get all loyalty program tiers
@router.get("/", response_model=List[LoyaltyProgram])
def get_all_loyalty_tiers(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    return db.query(LoyaltyProgramModel).filter(LoyaltyProgramModel.hotel_id == hotel_id).order_by(LoyaltyProgramModel.visit_count).all()


# Get active loyalty program tiers
@router.get("/active", response_model=List[LoyaltyProgram])
def get_active_loyalty_tiers(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    return (
        db.query(LoyaltyProgramModel)
        .filter(
            LoyaltyProgramModel.hotel_id == hotel_id,
            LoyaltyProgramModel.is_active == True
        )
        .order_by(LoyaltyProgramModel.visit_count)
        .all()
    )


# Get loyalty tier by ID
@router.get("/{tier_id}", response_model=LoyaltyProgram)
def get_loyalty_tier(tier_id: int, request: Request, db: Session = Depends(get_session_database)):
    db_tier = (
        db.query(LoyaltyProgramModel).filter(LoyaltyProgramModel.id == tier_id).first()
    )
    if not db_tier:
        raise HTTPException(status_code=404, detail="Loyalty tier not found")
    return db_tier


# Create new loyalty tier
@router.post("/", response_model=LoyaltyProgram)
def create_loyalty_tier(tier: LoyaltyProgramCreate, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Check if a tier with this visit count already exists for this hotel
    existing_tier = (
        db.query(LoyaltyProgramModel)
        .filter(
            LoyaltyProgramModel.hotel_id == hotel_id,
            LoyaltyProgramModel.visit_count == tier.visit_count
        )
        .first()
    )
    if existing_tier:
        raise HTTPException(
            status_code=400,
            detail=f"Loyalty tier with visit count {tier.visit_count} already exists",
        )

    # Create new tier
    db_tier = LoyaltyProgramModel(
        hotel_id=hotel_id,
        visit_count=tier.visit_count,
        discount_percentage=tier.discount_percentage,
        is_active=tier.is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_tier)
    db.commit()
    db.refresh(db_tier)
    return db_tier


# Update loyalty tier
@router.put("/{tier_id}", response_model=LoyaltyProgram)
def update_loyalty_tier(
    tier_id: int, tier_update: LoyaltyProgramUpdate, request: Request, db: Session = Depends(get_session_database)
):
    db_tier = (
        db.query(LoyaltyProgramModel).filter(LoyaltyProgramModel.id == tier_id).first()
    )
    if not db_tier:
        raise HTTPException(status_code=404, detail="Loyalty tier not found")

    # Check if updating visit count and if it already exists
    if (
        tier_update.visit_count is not None
        and tier_update.visit_count != db_tier.visit_count
    ):
        existing_tier = (
            db.query(LoyaltyProgramModel)
            .filter(
                LoyaltyProgramModel.visit_count == tier_update.visit_count,
                LoyaltyProgramModel.id != tier_id,
            )
            .first()
        )
        if existing_tier:
            raise HTTPException(
                status_code=400,
                detail=f"Loyalty tier with visit count {tier_update.visit_count} already exists",
            )
        db_tier.visit_count = tier_update.visit_count

    # Update other fields if provided
    if tier_update.discount_percentage is not None:
        db_tier.discount_percentage = tier_update.discount_percentage
    if tier_update.is_active is not None:
        db_tier.is_active = tier_update.is_active

    db_tier.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_tier)
    return db_tier


# Delete loyalty tier
@router.delete("/{tier_id}")
def delete_loyalty_tier(tier_id: int, request: Request, db: Session = Depends(get_session_database)):
    db_tier = (
        db.query(LoyaltyProgramModel).filter(LoyaltyProgramModel.id == tier_id).first()
    )
    if not db_tier:
        raise HTTPException(status_code=404, detail="Loyalty tier not found")

    db.delete(db_tier)
    db.commit()
    return {"message": "Loyalty tier deleted successfully"}


# Get applicable discount for a visit count
@router.get("/discount/{visit_count}")
def get_discount_for_visit_count(visit_count: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Find the tier that exactly matches the visit count for this hotel
    applicable_tier = (
        db.query(LoyaltyProgramModel)
        .filter(
            LoyaltyProgramModel.hotel_id == hotel_id,
            LoyaltyProgramModel.visit_count == visit_count,
            LoyaltyProgramModel.is_active == True,
        )
        .first()
    )

    if not applicable_tier:
        return {"discount_percentage": 0, "message": "No applicable loyalty discount"}

    return {
        "discount_percentage": applicable_tier.discount_percentage,
        "tier_id": applicable_tier.id,
        "visit_count": applicable_tier.visit_count,
        "message": f"Loyalty discount of {applicable_tier.discount_percentage}% applied for {visit_count} visits",
    }
