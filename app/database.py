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
from .config import settings

# Base declarative class
Base = declarative_base()

# Database engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)


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


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer, default=0)
    image_path = Column(String, nullable=True)
    discount = Column(Float, default=0)
    is_offer = Column(Integer, default=0)
    is_special = Column(Integer, default=0)
    is_vegetarian = Column(Integer, default=1)
    visibility = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="dishes")
    order_items = relationship("OrderItem", back_populates="dish")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    table_number = Column(Integer)
    unique_id = Column(String, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    status = Column(String, default="pending")
    total_amount = Column(Float, nullable=True)
    subtotal_amount = Column(Float, nullable=True)
    loyalty_discount_amount = Column(Float, default=0)
    selection_offer_discount_amount = Column(Float, default=0)
    loyalty_discount_percentage = Column(Float, default=0)
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
    phone_number = Column(String, index=True, nullable=True)
    visit_count = Column(Integer, default=0)
    last_visit = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Unique constraints per hotel
    __table_args__ = (
        UniqueConstraint("hotel_id", "username", name="uq_person_hotel_username"),
        UniqueConstraint("hotel_id", "phone_number", name="uq_person_hotel_phone"),
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
    price = Column(Float, nullable=True)
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
    rating = Column(Integer)
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
    visit_count = Column(Integer)
    discount_percentage = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Unique constraint per hotel
    __table_args__ = (
        UniqueConstraint("hotel_id", "visit_count", name="uq_loyalty_hotel_visits"),
    )

    # Relationships
    hotel = relationship("Hotel", back_populates="loyalty_tiers")


class SelectionOffer(Base):
    __tablename__ = "selection_offers"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, index=True)
    min_amount = Column(Float)
    discount_amount = Column(Float)
    is_active = Column(Boolean, default=True)
    description = Column(String, nullable=True)
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
    table_number = Column(Integer)
    is_occupied = Column(Boolean, default=False)
    current_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Unique constraint per hotel
    __table_args__ = (
        UniqueConstraint("hotel_id", "table_number", name="uq_table_hotel_number"),
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
    __table_args__ = (UniqueConstraint("hotel_id", name="uq_settings_hotel"),)

    # Relationships
    hotel = relationship("Hotel", back_populates="settings")


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified successfully")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
