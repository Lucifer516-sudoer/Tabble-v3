import sys
import os
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    engine,
)

def init_db(force_reset=False):
    """
    Initializes the database with a clean slate and sample data.
    Creates one sample hotel and populates it with sample dishes, tables, etc.
    """
    print("Initializing database...")

    if force_reset:
        print("Force resetting database: dropping all tables.")
        Base.metadata.drop_all(bind=engine)

    # Create all tables based on models
    create_tables()

    # Create a new database session
    db = SessionLocal()

    try:
        # Check if hotels already exist
        if db.query(Hotel).count() > 0 and not force_reset:
            print("Database already contains data. Skipping initialization.")
            return

        # 1. Create a Sample Hotel
        print("Creating sample hotel...")
        sample_hotel = Hotel(hotel_name="Tabble Inn", password="password123")
        db.add(sample_hotel)
        db.commit()
        db.refresh(sample_hotel)

        primary_hotel_id = sample_hotel.id
        print(f"Sample hotel 'Tabble Inn' created with ID: {primary_hotel_id}")

        # 2. Add Sample Dishes for the hotel
        print("Adding sample dishes...")
        sample_dishes = [
            Dish(hotel_id=primary_hotel_id, name="Margherita Pizza", description="Classic pizza with tomato sauce, mozzarella, and basil", category='["Main Course", "Italian"]', price=12.99, quantity=20, image_path="/static/images/default-dish.jpg", is_vegetarian=1),
            Dish(hotel_id=primary_hotel_id, name="Caesar Salad", description="Fresh romaine lettuce with Caesar dressing, croutons, and parmesan", category='["Appetizer", "Salad"]', price=8.99, quantity=15, image_path="/static/images/default-dish.jpg", is_vegetarian=1),
            Dish(hotel_id=primary_hotel_id, name="Chicken Alfredo", description="Fettuccine pasta with creamy Alfredo sauce and grilled chicken", category="Main Course", price=15.99, quantity=12, image_path="/static/images/default-dish.jpg", is_vegetarian=0),
            Dish(hotel_id=primary_hotel_id, name="Chocolate Lava Cake", description="Warm chocolate cake with a molten center", category="Dessert", price=8.99, quantity=15, image_path="/static/images/default-dish.jpg", is_vegetarian=1),
        ]
        db.add_all(sample_dishes)

        # 3. Add Sample Tables for the hotel
        print("Adding sample tables...")
        sample_tables = [Table(hotel_id=primary_hotel_id, table_number=i) for i in range(1, 9)]
        db.add_all(sample_tables)

        # 4. Add Sample Loyalty Program Tiers
        print("Adding sample loyalty tiers...")
        sample_loyalty_tiers = [
            LoyaltyProgram(hotel_id=primary_hotel_id, visit_count=5, discount_percentage=10.0),
            LoyaltyProgram(hotel_id=primary_hotel_id, visit_count=10, discount_percentage=15.0),
        ]
        db.add_all(sample_loyalty_tiers)

        # 5. Add Sample Selection Offers
        print("Adding sample selection offers...")
        sample_selection_offers = [
            SelectionOffer(hotel_id=primary_hotel_id, min_amount=50.0, discount_amount=5.0, description="Spend $50, get $5 off"),
            SelectionOffer(hotel_id=primary_hotel_id, min_amount=100.0, discount_amount=15.0, description="Spend $100, get $15 off"),
        ]
        db.add_all(sample_selection_offers)

        # Commit all changes to the database
        db.commit()

        print("\nDatabase initialized successfully with sample data for 'Tabble Inn'.")

    finally:
        # Close the session
        db.close()


if __name__ == "__main__":
    # Ensure the static images directory exists
    os.makedirs("app/static/images", exist_ok=True)

    # Check for a --force-reset flag in command-line arguments
    force = "--force-reset" in sys.argv

    # Run the initialization function
    init_db(force_reset=force)
