from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Text,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime, timezone
import os
import threading
from typing import Dict, Optional
import uuid

# Base declarative class
Base = declarative_base()

# Session-based database manager with hotel context
class DatabaseManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.lock = threading.Lock()
        self.unified_database = "Tabble.db"

    def get_session_id(self, request_headers: dict) -> str:
        """Generate or retrieve session ID from request headers"""
        session_id = request_headers.get('x-session-id')
        if not session_id:
            session_id = str(uuid.uuid4())
        return session_id

    def get_database_connection(self, session_id: str, hotel_id: Optional[int] = None) -> dict:
        """Get or create database connection for session with hotel context"""
        with self.lock:
            if session_id not in self.sessions:
                # Create new session with unified database
                self.sessions[session_id] = self._create_connection(hotel_id)
            elif hotel_id and self.sessions[session_id].get('hotel_id') != hotel_id:
                # Update hotel context for existing session
                self.sessions[session_id]['hotel_id'] = hotel_id

            return self.sessions[session_id]

    def _create_connection(self, hotel_id: Optional[int] = None) -> dict:
        """Create a new database connection to unified database"""
        database_url = f"sqlite:///./Tabble.db"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session_local = scoped_session(session_factory)

        # Create tables in the database if they don't exist
        Base.metadata.create_all(bind=engine)

        return {
            'database_name': self.unified_database,
            'database_url': database_url,
            'engine': engine,
            'session_local': session_local,
            'hotel_id': hotel_id
        }

    def _dispose_connection(self, session_id: str):
        """Dispose of database connection for session"""
        if session_id in self.sessions:
            connection = self.sessions[session_id]
            connection['session_local'].remove()
            connection['engine'].dispose()

    def set_hotel_context(self, session_id: str, hotel_id: int) -> bool:
        """Set hotel context for a specific session"""
        try:
            self.get_database_connection(session_id, hotel_id)
            print(f"Session {session_id} set to hotel_id: {hotel_id}")
            return True
        except Exception as e:
            print(f"Error setting hotel context for session {session_id}: {e}")
            return False

    def get_current_hotel_id(self, session_id: str) -> Optional[int]:
        """Get current hotel_id for session"""
        if session_id in self.sessions:
            return self.sessions[session_id].get('hotel_id')
        return None

    def get_current_database(self, session_id: str) -> str:
        """Get current database name for session (always Tabble.db)"""
        return self.unified_database

    def authenticate_hotel(self, hotel_name: str, password: str) -> Optional[int]:
        """Authenticate hotel and return hotel_id"""
        try:
            # Use global engine to query hotels table
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=engine)
            db = Session()

            hotel = db.query(Hotel).filter(
                Hotel.hotel_name == hotel_name,
                Hotel.password == password
            ).first()

            db.close()

            if hotel:
                return hotel.id
            return None
        except Exception as e:
            print(f"Error authenticating hotel {hotel_name}: {e}")
            return None

    def cleanup_session(self, session_id: str):
        """Clean up session resources"""
        with self.lock:
            if session_id in self.sessions:
                self._dispose_connection(session_id)
                del self.sessions[session_id]

# Global database manager instance
db_manager = DatabaseManager()

# Global variables for database connection (unified database)
CURRENT_DATABASE = "Tabble.db"
DATABASE_URL = f"sqlite:///./Tabble.db"  # Using the unified database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Lock for thread safety when switching databases
db_lock = threading.Lock()


# Database models
class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    dishes = relationship("Dish", back_populates="hotel")
    persons = relationship("Person", back_populates="hotel")
    orders = relationship("Order", back_populates="hotel")
    tables = relationship("Table", back_populates="hotel")
    settings = relationship("Settings", back_populates="hotel")
    feedback = relationship("Feedback", back_populates="hotel")
    loyalty_tiers = relationship("LoyaltyProgram", back_populates="hotel")
    selection_offers = relationship("SelectionOffer", back_populates="hotel")
    otp_requests = relationship("OtpRequest", back_populates="hotel")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, index=True)  # Now stores JSON array for multiple categories
    price = Column(Float)
    quantity = Column(Integer, default=0)  # Made optional in forms, but keeps default
    image_path = Column(String, nullable=True)
    discount = Column(Float, default=0)  # Discount amount (percentage)
    is_offer = Column(Integer, default=0)  # 0 = not an offer, 1 = is an offer
    is_special = Column(Integer, default=0)  # 0 = not special, 1 = today's special
    is_vegetarian = Column(Integer, default=1)  # 1 = vegetarian, 0 = non-vegetarian
    visibility = Column(Integer, default=1)  # 1 = visible, 0 = hidden (soft delete)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="dishes")

    # Relationship with OrderItem
    order_items = relationship("OrderItem", back_populates="dish")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    table_number = Column(Integer)
    unique_id = Column(String, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    status = Column(String, default="pending")  # pending, accepted, completed, paid
    total_amount = Column(Float, nullable=True)  # Final amount paid after all discounts
    subtotal_amount = Column(Float, nullable=True)  # Original amount before discounts
    loyalty_discount_amount = Column(Float, default=0)  # Loyalty discount applied
    selection_offer_discount_amount = Column(Float, default=0)  # Selection offer discount applied
    loyalty_discount_percentage = Column(Float, default=0)  # Loyalty discount percentage applied
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    person = relationship("Person", back_populates="orders")


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    username = Column(String, index=True)
    password = Column(String)
    phone_number = Column(String, index=True, nullable=True)  # Added phone number field
    visit_count = Column(Integer, default=0)
    last_visit = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Unique constraints per hotel
    __table_args__ = (
        UniqueConstraint('hotel_id', 'username', name='uq_person_hotel_username'),
        UniqueConstraint('hotel_id', 'phone_number', name='uq_person_hotel_phone'),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="persons")
    orders = relationship("Order", back_populates="person")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=True)  # Price at time of order
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    hotel = relationship("Hotel", back_populates="feedback")
    order = relationship("Order")
    person = relationship("Person")


class LoyaltyProgram(Base):
    __tablename__ = "loyalty_tiers"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    visit_count = Column(Integer)  # Number of visits required
    discount_percentage = Column(Float)  # Discount percentage
    is_active = Column(Boolean, default=True)  # Whether this loyalty tier is active
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Unique constraint per hotel
    __table_args__ = (
        UniqueConstraint('hotel_id', 'visit_count', name='uq_loyalty_hotel_visits'),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="loyalty_tiers")


class SelectionOffer(Base):
    __tablename__ = "selection_offers"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    min_amount = Column(Float)  # Minimum order amount to qualify
    discount_amount = Column(Float)  # Fixed discount amount to apply
    is_active = Column(Boolean, default=True)  # Whether this offer is active
    description = Column(String, nullable=True)  # Optional description of the offer
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="selection_offers")


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    table_number = Column(Integer)  # Table number
    is_occupied = Column(
        Boolean, default=False
    )  # Whether the table is currently occupied
    current_order_id = Column(
        Integer, ForeignKey("orders.id"), nullable=True
    )  # Current active order
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Unique constraint per hotel
    __table_args__ = (
        UniqueConstraint('hotel_id', 'table_number', name='uq_table_hotel_number'),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="tables")
    current_order = relationship("Order", foreign_keys=[current_order_id])


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    hotel_name = Column(String, nullable=False, default="Tabble Hotel")
    address = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    logo_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Unique constraint per hotel
    __table_args__ = (
        UniqueConstraint('hotel_id', name='uq_settings_hotel'),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="settings")


class OtpRequest(Base):
    __tablename__ = "otp_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    phone_number = Column(String, nullable=False, index=True)
    otp_code = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    verified = Column(Boolean, default=False)

    hotel = relationship("Hotel", back_populates="otp_requests")


# Function to switch database
def switch_database(database_name):
    global CURRENT_DATABASE, DATABASE_URL, engine, SessionLocal

    with db_lock:
        if database_name == CURRENT_DATABASE:
            return  # Already using this database

        # Update global variables
        CURRENT_DATABASE = database_name
        DATABASE_URL = f"sqlite:///./tabble_new.db" if database_name == "tabble_new.db" else f"sqlite:///./{database_name}"

        # Dispose of the old engine and create a new one
        engine.dispose()
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

        # Create a new session factory and scoped session
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        SessionLocal.remove()
        SessionLocal = scoped_session(session_factory)

        # Create tables in the new database if they don't exist
        create_tables()

        print(f"Switched to database: {database_name}")


# Get current database name
def get_current_database():
    return CURRENT_DATABASE


# Create tables
def create_tables():
    # Create all tables (only creates tables that don't exist)
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified successfully")


# Get database session (legacy)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Session-aware database functions with hotel context
def get_session_db(session_id: str, hotel_id: Optional[int] = None):
    """Get database session for a specific session ID with hotel context"""
    connection = db_manager.get_database_connection(session_id, hotel_id)
    db = connection['session_local']()
    try:
        yield db
    finally:
        db.close()


def set_session_hotel_context(session_id: str, hotel_id: int) -> bool:
    """Set hotel context for a specific session"""
    return db_manager.set_hotel_context(session_id, hotel_id)


def get_session_hotel_id(session_id: str) -> Optional[int]:
    """Get current hotel_id for a session"""
    return db_manager.get_current_hotel_id(session_id)


def get_session_current_database(session_id: str) -> str:
    """Get current database name for a session (always Tabble.db)"""
    return db_manager.get_current_database(session_id)


def authenticate_hotel_session(hotel_name: str, password: str) -> Optional[int]:
    """Authenticate hotel and return hotel_id"""
    return db_manager.authenticate_hotel(hotel_name, password)


def cleanup_session_db(session_id: str):
    """Clean up database resources for a session"""
    db_manager.cleanup_session(session_id)


# Helper function to get hotel_id from request
def get_hotel_id_from_request(request) -> int:
    """Get hotel_id from request session, raise HTTPException if not found"""
    from fastapi import HTTPException
    from .middleware import get_session_id

    session_id = get_session_id(request)
    hotel_id = get_session_hotel_id(session_id)

    if not hotel_id:
        raise HTTPException(status_code=400, detail="No hotel context set")

    return hotel_id
