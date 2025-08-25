from app.database import (
    create_tables,
    SessionLocal,
    Dish,
    Person,
    Base,
    LoyaltyProgram,
    SelectionOffer,
    Table,
    Hotel,
)
from sqlalchemy import create_engine
from datetime import datetime, timezone
import os
from app.config import settings


def init_db():
    # Create tables
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    create_tables()

    # Create a database session
    db = SessionLocal()

    # Check if hotels already exist
    existing_hotels = db.query(Hotel).count()
    if existing_hotels > 0:
        print("Database already contains data. Skipping initialization.")
        return

    # Add sample hotel
    sample_hotel = Hotel(
        hotel_name="Tabble Hotel",
        password="password123",
    )
    db.add(sample_hotel)
    db.commit()
    db.refresh(sample_hotel)

    # Add sample dishes
    sample_dishes = [
        # Regular dishes
        Dish(
            hotel_id=sample_hotel.id,
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce, mozzarella, and basil",
            category='["Main Course", "Italian"]',
            price=12.99,
            quantity=20,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
            is_vegetarian=1,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Caesar Salad",
            description="Fresh romaine lettuce with Caesar dressing, croutons, and parmesan",
            category='["Appetizer", "Salad"]',
            price=8.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
            is_vegetarian=1,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Chocolate Cake",
            description="Rich chocolate cake with ganache frosting",
            category="Dessert",
            price=6.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Iced Tea",
            description="Refreshing iced tea with lemon",
            category="Beverage",
            price=3.99,
            quantity=30,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Chicken Alfredo",
            description="Fettuccine pasta with creamy Alfredo sauce and grilled chicken",
            category="Main Course",
            price=15.99,
            quantity=12,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Garlic Bread",
            description="Toasted bread with garlic butter and herbs",
            category="Appetizer",
            price=4.99,
            quantity=25,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        # Special offer dishes
        Dish(
            hotel_id=sample_hotel.id,
            name="Weekend Special Pizza",
            description="Deluxe pizza with premium toppings and extra cheese",
            category="Main Course",
            price=18.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg",
            discount=20,
            is_offer=1,
            is_special=0,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Seafood Pasta",
            description="Fresh pasta with mixed seafood in a creamy sauce",
            category="Main Course",
            price=22.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg",
            discount=15,
            is_offer=1,
            is_special=0,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Tiramisu",
            description="Classic Italian dessert with coffee-soaked ladyfingers and mascarpone cream",
            category="Dessert",
            price=9.99,
            quantity=8,
            image_path="/static/images/default-dish.jpg",
            discount=25,
            is_offer=1,
            is_special=0,
        ),
        # Today's special dishes
        Dish(
            hotel_id=sample_hotel.id,
            name="Chef's Special Steak",
            description="Prime cut steak cooked to perfection with special house seasoning",
            category="Main Course",
            price=24.99,
            quantity=12,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=1,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Truffle Mushroom Risotto",
            description="Creamy risotto with wild mushrooms and truffle oil",
            category="Main Course",
            price=16.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=1,
        ),
        Dish(
            hotel_id=sample_hotel.id,
            name="Chocolate Lava Cake",
            description="Warm chocolate cake with a molten center, served with vanilla ice cream",
            category="Dessert",
            price=8.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=1,
        ),
    ]

    # Add dishes to database
    for dish in sample_dishes:
        db.add(dish)

    # Add sample users
    sample_users = [
        Person(
            hotel_id=sample_hotel.id,
            username="john_doe",
            password="password123",
            visit_count=1,
            last_visit=datetime.now(timezone.utc),
        ),
        Person(
            hotel_id=sample_hotel.id,
            username="jane_smith",
            password="password456",
            visit_count=3,
            last_visit=datetime.now(timezone.utc),
        ),
        Person(
            hotel_id=sample_hotel.id,
            username="guest",
            password="guest",
            visit_count=5,
            last_visit=datetime.now(timezone.utc),
        ),
    ]

    # Add users to database
    for user in sample_users:
        db.add(user)

    # Add sample loyalty program tiers
    sample_loyalty_tiers = [
        LoyaltyProgram(
            hotel_id=sample_hotel.id,
            visit_count=3,
            discount_percentage=5.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        LoyaltyProgram(
            hotel_id=sample_hotel.id,
            visit_count=5,
            discount_percentage=10.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        LoyaltyProgram(
            hotel_id=sample_hotel.id,
            visit_count=10,
            discount_percentage=15.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        LoyaltyProgram(
            hotel_id=sample_hotel.id,
            visit_count=20,
            discount_percentage=20.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    # Add loyalty tiers to database
    for tier in sample_loyalty_tiers:
        db.add(tier)

    # Add sample selection offers
    sample_selection_offers = [
        SelectionOffer(
            hotel_id=sample_hotel.id,
            min_amount=50.0,
            discount_amount=5.0,
            is_active=True,
            description="Spend $50, get $5 off",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SelectionOffer(
            hotel_id=sample_hotel.id,
            min_amount=100.0,
            discount_amount=15.0,
            is_active=True,
            description="Spend $100, get $15 off",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SelectionOffer(
            hotel_id=sample_hotel.id,
            min_amount=150.0,
            discount_amount=25.0,
            is_active=True,
            description="Spend $150, get $25 off",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    # Add selection offers to database
    for offer in sample_selection_offers:
        db.add(offer)

    # Add sample tables
    sample_tables = [
        Table(
            hotel_id=sample_hotel.id,
            table_number=1,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=2,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=3,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=4,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=5,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=6,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=7,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            hotel_id=sample_hotel.id,
            table_number=8,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    # Add tables to database
    for table in sample_tables:
        db.add(table)

    # Commit changes
    db.commit()

    print("Database initialized with sample data:")
    print("- Added", len(sample_dishes), "sample dishes")
    print("- Added", len(sample_users), "sample users")
    print("- Added", len(sample_loyalty_tiers), "loyalty program tiers")
    print("- Added", len(sample_selection_offers), "selection offers")
    print("- Added", len(sample_tables), "tables")

    # Close session
    db.close()


if __name__ == "__main__":
    # Create static/images directory if it doesn't exist
    os.makedirs("app/static/images", exist_ok=True)

    # Initialize database
    init_db()
