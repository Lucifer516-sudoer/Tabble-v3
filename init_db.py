from app.database import (
    create_tables,
    SessionLocal,
    Dish,
    Person,
    Base,
    LoyaltyProgram,
    SelectionOffer,
    Table,
    Hotel,  # Import Hotel model
    engine, # Import engine to get the correct database
)
from datetime import datetime, timezone
import os
import sys


def init_db(force_reset=False):
    # Check if force_reset is enabled
    if force_reset:
        # Drop all tables and recreate them
        print("Forcing database reset...")
        Base.metadata.drop_all(bind=engine)

    # Create tables
    create_tables()

    # Create a database session
    db = SessionLocal()

    # Check if hotels already exist
    existing_hotels = db.query(Hotel).count()
    if existing_hotels > 0 and not force_reset:
        print("Database already contains hotels. Skipping initialization.")
        return

    # Add sample hotels from the old hotels.csv
    sample_hotels = [
        {'hotel_name': 'tabble_new', 'password': 'myhotel'},
        {'hotel_name': 'anifa', 'password': 'anifa123'},
        {'hotel_name': 'hotelgood', 'password': 'hotelgood123'},
        {'hotel_name': 'hotelmoon', 'password': 'moon123'},
        {'hotel_name': 'shine', 'password': 'shine123'},
    ]

    new_hotels = []
    for hotel_data in sample_hotels:
        hotel = Hotel(hotel_name=hotel_data['hotel_name'], password=hotel_data['password'])
        db.add(hotel)
        new_hotels.append(hotel)

    db.commit()

    # Get the ID of the first hotel to associate sample data with it
    primary_hotel_id = new_hotels[0].id
    print(f"Added {len(new_hotels)} hotels. Sample data will be associated with hotel_id: {primary_hotel_id}")


    # Add sample dishes
    sample_dishes = [
        Dish(hotel_id=primary_hotel_id, name="Margherita Pizza", description="Classic pizza with tomato sauce, mozzarella, and basil", category='["Main Course", "Italian"]', price=12.99, quantity=20, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=0, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Caesar Salad", description="Fresh romaine lettuce with Caesar dressing, croutons, and parmesan", category='["Appetizer", "Salad"]', price=8.99, quantity=15, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=0, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Chocolate Cake", description="Rich chocolate cake with ganache frosting", category='Dessert', price=6.99, quantity=10, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=0, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Iced Tea", description="Refreshing iced tea with lemon", category='Beverage', price=3.99, quantity=30, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=0, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Chicken Alfredo", description="Fettuccine pasta with creamy Alfredo sauce and grilled chicken", category='Main Course', price=15.99, quantity=12, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_vegetarian=0),
        Dish(hotel_id=primary_hotel_id, name="Garlic Bread", description="Toasted bread with garlic butter and herbs", category='Appetizer', price=4.99, quantity=25, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=0, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Weekend Special Pizza", description="Deluxe pizza with premium toppings and extra cheese", category='Main Course', price=18.99, quantity=15, image_path="/static/images/default-dish.jpg", discount=20, is_offer=1, is_special=0, is_vegetarian=0),
        Dish(hotel_id=primary_hotel_id, name="Seafood Pasta", description="Fresh pasta with mixed seafood in a creamy sauce", category='Main Course', price=22.99, quantity=10, image_path="/static/images/default-dish.jpg", discount=15, is_offer=1, is_special=0, is_vegetarian=0),
        Dish(hotel_id=primary_hotel_id, name="Tiramisu", description="Classic Italian dessert with coffee-soaked ladyfingers and mascarpone cream", category='Dessert', price=9.99, quantity=8, image_path="/static/images/default-dish.jpg", discount=25, is_offer=1, is_special=0, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Chef's Special Steak", description="Prime cut steak cooked to perfection with special house seasoning", category='Main Course', price=24.99, quantity=12, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=1, is_vegetarian=0),
        Dish(hotel_id=primary_hotel_id, name="Truffle Mushroom Risotto", description="Creamy risotto with wild mushrooms and truffle oil", category='Main Course', price=16.99, quantity=10, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=1, is_vegetarian=1),
        Dish(hotel_id=primary_hotel_id, name="Chocolate Lava Cake", description="Warm chocolate cake with a molten center, served with vanilla ice cream", category='Dessert', price=8.99, quantity=15, image_path="/static/images/default-dish.jpg", discount=0, is_offer=0, is_special=1, is_vegetarian=1),
    ]
    for dish in sample_dishes:
        db.add(dish)

    # Add sample users
    sample_users = [
        Person(hotel_id=primary_hotel_id, username="john_doe", password="password123", visit_count=1, last_visit=datetime.now(timezone.utc)),
        Person(hotel_id=primary_hotel_id, username="jane_smith", password="password456", visit_count=3, last_visit=datetime.now(timezone.utc)),
        Person(hotel_id=primary_hotel_id, username="guest", password="guest", visit_count=5, last_visit=datetime.now(timezone.utc)),
    ]
    for user in sample_users:
        db.add(user)

    # Add sample loyalty program tiers
    sample_loyalty_tiers = [
        LoyaltyProgram(hotel_id=primary_hotel_id, visit_count=3, discount_percentage=5.0, is_active=True),
        LoyaltyProgram(hotel_id=primary_hotel_id, visit_count=5, discount_percentage=10.0, is_active=True),
        LoyaltyProgram(hotel_id=primary_hotel_id, visit_count=10, discount_percentage=15.0, is_active=True),
        LoyaltyProgram(hotel_id=primary_hotel_id, visit_count=20, discount_percentage=20.0, is_active=True),
    ]
    for tier in sample_loyalty_tiers:
        db.add(tier)

    # Add sample selection offers
    sample_selection_offers = [
        SelectionOffer(hotel_id=primary_hotel_id, min_amount=50.0, discount_amount=5.0, is_active=True, description="Spend $50, get $5 off"),
        SelectionOffer(hotel_id=primary_hotel_id, min_amount=100.0, discount_amount=15.0, is_active=True, description="Spend $100, get $15 off"),
        SelectionOffer(hotel_id=primary_hotel_id, min_amount=150.0, discount_amount=25.0, is_active=True, description="Spend $150, get $25 off"),
    ]
    for offer in sample_selection_offers:
        db.add(offer)

    # Add sample tables
    sample_tables = [
        Table(hotel_id=primary_hotel_id, table_number=1, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=2, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=3, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=4, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=5, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=6, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=7, is_occupied=False),
        Table(hotel_id=primary_hotel_id, table_number=8, is_occupied=False),
    ]
    for table in sample_tables:
        db.add(table)

    db.commit()

    print("Database initialized with sample data:")
    print(f"- Added {len(sample_hotels)} sample hotels")
    print(f"- Added {len(sample_dishes)} sample dishes to hotel_id={primary_hotel_id}")
    print(f"- Added {len(sample_users)} sample users to hotel_id={primary_hotel_id}")
    print(f"- Added {len(sample_loyalty_tiers)} loyalty program tiers to hotel_id={primary_hotel_id}")
    print(f"- Added {len(sample_selection_offers)} selection offers to hotel_id={primary_hotel_id}")
    print(f"- Added {len(sample_tables)} tables to hotel_id={primary_hotel_id}")

    db.close()


if __name__ == "__main__":
    os.makedirs("app/static/images", exist_ok=True)
    force_reset = "--force-reset" in sys.argv
    init_db(force_reset)
