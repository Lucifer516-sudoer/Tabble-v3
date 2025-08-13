from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta

from ..database import get_db, Dish, Order, OrderItem, Person, get_session_db, get_hotel_id_from_request
from ..models.dish import Dish as DishModel
from ..models.order import OrderCreate, Order as OrderModel
from ..models.user import (
    PersonCreate,
    PersonLogin,
    Person as PersonModel,
    PhoneAuthRequest,
    PhoneVerifyRequest,
    UsernameRequest
)
from ..services import otp_service
from ..middleware import get_session_id

router = APIRouter(
    prefix="/customer",
    tags=["customer"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    return next(get_session_db(session_id))


# Get all dishes for menu (only visible ones)
@router.get("/api/menu", response_model=List[DishModel])
def get_menu(request: Request, category: str = None, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    if category:
        # Filter dishes that contain the specified category in their JSON array
        import json
        all_dishes = db.query(Dish).filter(
            Dish.hotel_id == hotel_id,
            Dish.visibility == 1
        ).all()

        filtered_dishes = []
        for dish in all_dishes:
            try:
                dish_categories = json.loads(dish.category) if dish.category else []
                if isinstance(dish_categories, list) and category in dish_categories:
                    filtered_dishes.append(dish)
                elif isinstance(dish_categories, str) and dish_categories == category:
                    filtered_dishes.append(dish)
            except (json.JSONDecodeError, TypeError):
                # Backward compatibility: treat as single category
                if dish.category == category:
                    filtered_dishes.append(dish)

        return filtered_dishes
    else:
        dishes = db.query(Dish).filter(
            Dish.hotel_id == hotel_id,
            Dish.visibility == 1
        ).all()
        return dishes


# Get offer dishes (only visible ones)
@router.get("/api/offers", response_model=List[DishModel])
def get_offers(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    dishes = db.query(Dish).filter(
        Dish.hotel_id == hotel_id,
        Dish.is_offer == 1,
        Dish.visibility == 1
    ).all()
    return dishes


# Get special dishes (only visible ones)
@router.get("/api/specials", response_model=List[DishModel])
def get_specials(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    dishes = db.query(Dish).filter(
        Dish.hotel_id == hotel_id,
        Dish.is_special == 1,
        Dish.visibility == 1
    ).all()
    return dishes


# Get all dish categories (only from visible dishes)
@router.get("/api/categories")
def get_categories(request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)
    categories = db.query(Dish.category).filter(
        Dish.hotel_id == hotel_id,
        Dish.visibility == 1
    ).distinct().all()

    # Parse JSON categories and flatten them
    import json
    unique_categories = set()

    for category_tuple in categories:
        category_str = category_tuple[0]
        if category_str:
            try:
                # Try to parse as JSON array
                category_list = json.loads(category_str)
                if isinstance(category_list, list):
                    unique_categories.update(category_list)
                else:
                    unique_categories.add(category_str)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as single category
                unique_categories.add(category_str)

    return sorted(list(unique_categories))


# Register a new user or update existing user
@router.post("/api/register", response_model=PersonModel)
def register_user(user: PersonCreate, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Check if user already exists for this hotel
    db_user = db.query(Person).filter(
        Person.hotel_id == hotel_id,
        Person.username == user.username
    ).first()

    if db_user:
        # Update existing user's last visit time (visit count updated only when order is placed)
        db_user.last_visit = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        # Create new user (visit count will be incremented when first order is placed)
        db_user = Person(
            hotel_id=hotel_id,
            username=user.username,
            password=user.password,  # In a real app, you should hash this password
            visit_count=0,
            last_visit=datetime.now(timezone.utc),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


# Login user
@router.post("/api/login", response_model=Dict[str, Any])
def login_user(user_data: PersonLogin, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Find user by username for this hotel
    db_user = db.query(Person).filter(
        Person.hotel_id == hotel_id,
        Person.username == user_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
        )

    # Check password (in a real app, you would verify hashed passwords)
    if db_user.password != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    # Update last visit time (but not visit count - that's only updated when order is placed)
    db_user.last_visit = datetime.now(timezone.utc)
    db.commit()

    # Return user info and a success message
    return {
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "visit_count": db_user.visit_count,
        },
        "message": "Login successful",
    }


# Create new order
@router.post("/api/orders", response_model=OrderModel)
def create_order(
    order: OrderCreate, request: Request, person_id: int = Query(None), db: Session = Depends(get_session_database)
):
    hotel_id = get_hotel_id_from_request(request)

    # If person_id is not provided but we have a username/password, try to find or create the user
    if not person_id and hasattr(order, "username") and hasattr(order, "password"):
        # Check if user exists for this hotel
        db_user = db.query(Person).filter(
            Person.hotel_id == hotel_id,
            Person.username == order.username
        ).first()

        if db_user:
            # Update existing user's visit count
            db_user.visit_count += 1
            db_user.last_visit = datetime.now(timezone.utc)
            db.commit()
            person_id = db_user.id
        else:
            # Create new user (visit count starts at 1 since they're placing their first order)
            db_user = Person(
                hotel_id=hotel_id,
                username=order.username,
                password=order.password,
                visit_count=1,
                last_visit=datetime.now(timezone.utc),
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            person_id = db_user.id
    elif person_id:
        # If person_id is provided (normal flow), increment visit count for that user
        db_user = db.query(Person).filter(
            Person.hotel_id == hotel_id,
            Person.id == person_id
        ).first()
        if db_user:
            db_user.visit_count += 1
            db_user.last_visit = datetime.now(timezone.utc)
            db.commit()

    # Create order
    db_order = Order(
        hotel_id=hotel_id,
        table_number=order.table_number,
        unique_id=order.unique_id,
        person_id=person_id,  # Link order to person if provided
        status="pending",
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Mark the table as occupied
    from ..database import Table

    db_table = db.query(Table).filter(
        Table.hotel_id == hotel_id,
        Table.table_number == order.table_number
    ).first()
    if db_table:
        db_table.is_occupied = True
        db_table.current_order_id = db_order.id
        db.commit()

    # Create order items
    for item in order.items:
        # Get the dish to include its information and verify it belongs to this hotel
        dish = db.query(Dish).filter(
            Dish.hotel_id == hotel_id,
            Dish.id == item.dish_id
        ).first()
        if not dish:
            continue  # Skip if dish doesn't exist or doesn't belong to this hotel

        db_item = OrderItem(
            hotel_id=hotel_id,
            order_id=db_order.id,
            dish_id=item.dish_id,
            quantity=item.quantity,
            price=dish.price,  # Store price at time of order
            remarks=item.remarks,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return db_order


# Get order status
@router.get("/api/orders/{order_id}", response_model=OrderModel)
def get_order(order_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Use joinedload to load the dish relationship for each order item
    order = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.id == order_id
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Explicitly load dish information for each order item
    for item in order.items:
        if not hasattr(item, "dish") or item.dish is None:
            dish = db.query(Dish).filter(
                Dish.hotel_id == hotel_id,
                Dish.id == item.dish_id
            ).first()
            if dish:
                item.dish = dish

    return order


# Get orders by person_id
@router.get("/api/person/{person_id}/orders", response_model=List[OrderModel])
def get_person_orders(person_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    # Get all orders for a specific person in this hotel
    orders = (
        db.query(Order)
        .filter(
            Order.hotel_id == hotel_id,
            Order.person_id == person_id
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    # Explicitly load dish information for each order item
    for order in orders:
        for item in order.items:
            if not hasattr(item, "dish") or item.dish is None:
                dish = db.query(Dish).filter(
                    Dish.hotel_id == hotel_id,
                    Dish.id == item.dish_id
                ).first()
                if dish:
                    item.dish = dish

    return orders


# Request payment for order
@router.put("/api/orders/{order_id}/payment")
def request_payment(order_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    try:
        # Check if order exists and is not already paid
        db_order = db.query(Order).filter(
            Order.hotel_id == hotel_id,
            Order.id == order_id
        ).first()
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        # Check if order is already paid
        if db_order.status == "paid":
            return {"message": "Order is already paid"}

        # Check if order is completed (ready for payment)
        if db_order.status != "completed":
            raise HTTPException(
                status_code=400,
                detail="Order must be completed before payment can be processed"
            )

        # Calculate order totals and apply discounts
        from ..database import LoyaltyProgram, SelectionOffer, Person

        # Calculate subtotal from order items
        subtotal = 0
        for item in db_order.items:
            if item.dish:
                subtotal += item.dish.price * item.quantity

        # Initialize discount amounts
        loyalty_discount_amount = 0
        loyalty_discount_percentage = 0
        selection_offer_discount_amount = 0

        # Apply loyalty discount if customer is registered
        if db_order.person_id:
            person = db.query(Person).filter(Person.id == db_order.person_id).first()
            if person:
                # Get applicable loyalty discount
                loyalty_tier = (
                    db.query(LoyaltyProgram)
                    .filter(
                        LoyaltyProgram.hotel_id == hotel_id,
                        LoyaltyProgram.visit_count == person.visit_count,
                        LoyaltyProgram.is_active == True,
                    )
                    .first()
                )

                if loyalty_tier:
                    loyalty_discount_percentage = loyalty_tier.discount_percentage
                    loyalty_discount_amount = subtotal * (loyalty_discount_percentage / 100)

        # Apply selection offer discount
        selection_offer = (
            db.query(SelectionOffer)
            .filter(
                SelectionOffer.hotel_id == hotel_id,
                SelectionOffer.min_amount <= subtotal,
                SelectionOffer.is_active == True,
            )
            .order_by(SelectionOffer.min_amount.desc())
            .first()
        )

        if selection_offer:
            selection_offer_discount_amount = selection_offer.discount_amount

        # Calculate final total after discounts
        final_total = subtotal - loyalty_discount_amount - selection_offer_discount_amount

        # Ensure final total is not negative
        final_total = max(0, final_total)

        # Update order with calculated amounts
        db_order.status = "paid"
        db_order.subtotal_amount = subtotal
        db_order.loyalty_discount_amount = loyalty_discount_amount
        db_order.loyalty_discount_percentage = loyalty_discount_percentage
        db_order.selection_offer_discount_amount = selection_offer_discount_amount
        db_order.total_amount = final_total
        db_order.updated_at = datetime.now(timezone.utc)

        # Check if this is the last unpaid order for this table
        from ..database import Table

        # Get all orders for this table that are not paid
        table_unpaid_orders = db.query(Order).filter(
            Order.table_number == db_order.table_number,
            Order.status != "paid",
            Order.status != "cancelled"
        ).all()

        # If this is the only unpaid order, mark table as free
        if len(table_unpaid_orders) == 1 and table_unpaid_orders[0].id == order_id:
            db_table = db.query(Table).filter(Table.table_number == db_order.table_number).first()
            if db_table:
                db_table.is_occupied = False
                db_table.current_order_id = None
                db_table.updated_at = datetime.now(timezone.utc)

        # Commit the transaction
        db.commit()
        db.refresh(db_order)

        return {"message": "Payment completed successfully", "order_id": order_id}

    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        # Handle any other exceptions
        db.rollback()
        print(f"Error processing payment for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing payment: {str(e)}"
        )


# Cancel order
@router.put("/api/orders/{order_id}/cancel")
def cancel_order(order_id: int, request: Request, db: Session = Depends(get_session_database)):
    hotel_id = get_hotel_id_from_request(request)

    db_order = db.query(Order).filter(
        Order.hotel_id == hotel_id,
        Order.id == order_id
    ).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if order is in pending status (not accepted or completed)
    if db_order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be cancelled. Orders that have been accepted by the chef cannot be cancelled."
        )

    # Update order status to cancelled
    current_time = datetime.now(timezone.utc)
    db_order.status = "cancelled"
    db_order.updated_at = current_time

    # Mark the table as free if this was the current order
    from ..database import Table

    db_table = db.query(Table).filter(Table.table_number == db_order.table_number).first()
    if db_table and db_table.current_order_id == db_order.id:
        db_table.is_occupied = False
        db_table.current_order_id = None
        db_table.updated_at = current_time

    db.commit()

    return {"message": "Order cancelled successfully"}


# Get person details
@router.get("/api/person/{person_id}", response_model=PersonModel)
def get_person(person_id: int, request: Request, db: Session = Depends(get_session_database)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


# Phone authentication endpoints
@router.post("/api/phone-auth", response_model=Dict[str, Any])
async def phone_auth(auth_request: PhoneAuthRequest, request: Request, db: Session = Depends(get_session_database)):
    """
    Initiate phone authentication by sending OTP
    """
    try:
        hotel_id = get_hotel_id_from_request(request)
        if not hotel_id:
            raise HTTPException(status_code=400, detail="No hotel context set")

        # Send OTP via our new service
        token = await otp_service.send_otp(
            db=db,
            phone_number=auth_request.phone_number,
            hotel_id=hotel_id
        )

        print(f"Phone auth initiated for: {auth_request.phone_number}, table: {auth_request.table_number}")

        return {
            "success": True,
            "message": "Verification code sent successfully",
            "token": token
        }
    except HTTPException as e:
        print(f"HTTP Exception in phone_auth: {e.detail}")
        raise e
    except Exception as e:
        print(f"Exception in phone_auth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )


@router.post("/api/verify-otp", response_model=Dict[str, Any])
def verify_otp(verify_request: PhoneVerifyRequest, request: Request, db: Session = Depends(get_session_database)):
    """
    Verify OTP and authenticate user
    """
    try:
        print(f"Verifying OTP for phone: {verify_request.phone_number}")

        # Verify OTP via our new service
        otp_service.verify_otp(
            db=db,
            token=verify_request.token,
            otp=verify_request.verification_code,
            phone_number=verify_request.phone_number
        )

        # If verify_otp succeeds, proceed with the original logic.
        # Check if user exists in database for this hotel
        hotel_id = get_hotel_id_from_request(request)
        user = db.query(Person).filter(
            Person.hotel_id == hotel_id,
            Person.phone_number == verify_request.phone_number
        ).first()

        if user:
            print(f"Existing user found: {user.username}")
            # Existing user - update last visit time (visit count updated only when order is placed)
            user.last_visit = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)

            return {
                "success": True,
                "message": "Authentication successful",
                "user_exists": True,
                "user_id": user.id,
                "username": user.username
            }
        else:
            print(f"New user with phone: {verify_request.phone_number}")
            # New user - return flag to collect username
            return {
                "success": True,
                "message": "Authentication successful, but user not found",
                "user_exists": False
            }

    except HTTPException as e:
        print(f"HTTP Exception in verify_otp: {e.detail}")
        raise e
    except Exception as e:
        print(f"Exception in verify_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )


@router.post("/api/register-phone-user", response_model=Dict[str, Any])
def register_phone_user(user_request: UsernameRequest, request: Request, db: Session = Depends(get_session_database)):
    """
    Register a new user after phone authentication
    """
    try:
        hotel_id = get_hotel_id_from_request(request)
        print(f"Registering new user with phone: {user_request.phone_number}, username: {user_request.username}")

        # Check if username already exists for this hotel
        existing_user = db.query(Person).filter(
            Person.hotel_id == hotel_id,
            Person.username == user_request.username
        ).first()
        if existing_user:
            print(f"Username already exists: {user_request.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if phone number already exists for this hotel
        phone_user = db.query(Person).filter(
            Person.hotel_id == hotel_id,
            Person.phone_number == user_request.phone_number
        ).first()
        if phone_user:
            print(f"Phone number already registered: {user_request.phone_number}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # Create new user (visit count will be incremented when first order is placed)
        new_user = Person(
            hotel_id=hotel_id,
            username=user_request.username,
            password="",  # No password needed for phone auth
            phone_number=user_request.phone_number,
            visit_count=0,
            last_visit=datetime.now(timezone.utc)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"User registered successfully: {new_user.id}, {new_user.username}")

        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": new_user.id,
            "username": new_user.username
        }

    except HTTPException as e:
        print(f"HTTP Exception in register_phone_user: {e.detail}")
        raise e
    except Exception as e:
        print(f"Exception in register_phone_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )
