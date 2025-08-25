from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import Dish, Order, OrderItem, get_session_db, get_hotel_id_from_request
from ..models.dish import Dish as DishModel
from ..models.order import Order as OrderModel
from ..middleware import get_session_id

router = APIRouter(
    prefix="/chef",
    tags=["chef"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    return next(get_session_db(session_id))

# Add an API endpoint to get completed orders count
@router.get("/api/completed-orders-count")
def get_completed_orders_count(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    completed_orders = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.status == "completed"
    ).count()
    return {"count": completed_orders}

# Get pending orders (orders that need to be accepted)
@router.get("/orders/pending", response_model=List[OrderModel])
def get_pending_orders(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    orders = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.status == "pending"
    ).all()
    return orders

# Get accepted orders (orders that have been accepted but not completed)
@router.get("/orders/accepted", response_model=List[OrderModel])
def get_accepted_orders(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    orders = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.status == "accepted"
    ).all()
    return orders

# Accept an order
@router.put("/orders/{order_id}/accept")
def accept_order(order_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    db_order = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.id == order_id
    ).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status != "pending":
        raise HTTPException(status_code=400, detail="Order is not in pending status")

    db_order.status = "accepted"
    db_order.updated_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Order accepted successfully"}

# Mark order as completed (only accepted orders can be completed)
@router.put("/orders/{order_id}/complete")
def complete_order(order_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    db_order = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.id == order_id
    ).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status != "accepted":
        raise HTTPException(status_code=400, detail="Order must be accepted before it can be completed")

    db_order.status = "completed"
    db_order.updated_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Order marked as completed"}
