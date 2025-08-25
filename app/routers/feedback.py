from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import Feedback as FeedbackModel, Order, Person, get_session_db, get_hotel_id_from_request
from ..models.feedback import Feedback, FeedbackCreate
from ..middleware import get_session_id

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    return next(get_session_db(session_id))


# Create new feedback
@router.post("/", response_model=Feedback)
def create_feedback(feedback: FeedbackCreate, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Check if order exists for this hotel
    db_order = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.id == feedback.order_id
    ).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if person exists if person_id is provided
    if feedback.person_id:
        db_person = db.query(Person).filter(
            Person.hotel_id == hotel_id,
            Person.id == feedback.person_id
        ).first()
        if not db_person:
            raise HTTPException(status_code=404, detail="Person not found")

    # Create feedback
    db_feedback = FeedbackModel(
        hotel_id=hotel_id,
        order_id=feedback.order_id,
        person_id=feedback.person_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=datetime.now(timezone.utc),
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


# Get all feedback
@router.get("/", response_model=List[Feedback])
def get_all_feedback(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    return db.query(FeedbackModel).filter(FeedbackModel.hotel_id == hotel_id).all()


# Get feedback by order_id
@router.get("/order/{order_id}", response_model=Feedback)
def get_feedback_by_order(order_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    db_feedback = db.query(FeedbackModel).filter(
        FeedbackModel.hotel_id == hotel_id,
        FeedbackModel.order_id == order_id
    ).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback


# Get feedback by person_id
@router.get("/person/{person_id}", response_model=List[Feedback])
def get_feedback_by_person(person_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    return db.query(FeedbackModel).filter(
        FeedbackModel.hotel_id == hotel_id,
        FeedbackModel.person_id == person_id
    ).all()
