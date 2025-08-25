from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
import calendar

from ..database import get_db, Dish, Order, OrderItem, Person, Table, Feedback
from ..models.dish import Dish as DishModel
from ..models.order import Order as OrderModel
from ..models.user import Person as PersonModel
from ..models.feedback import Feedback as FeedbackModel

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)


# Get overall dashboard statistics
@router.get("/dashboard")
def get_dashboard_stats(
    request: Request,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    # Parse date strings to datetime objects if provided
    start_datetime = None
    end_datetime = None

    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    # Base query for orders
    orders_query = db.query(Order)

    # Apply date filters if provided
    if start_datetime:
        orders_query = orders_query.filter(Order.created_at >= start_datetime)

    if end_datetime:
        orders_query = orders_query.filter(Order.created_at <= end_datetime)

    # Total sales
    total_sales_query = (
        db.query(
            func.sum(Dish.price * OrderItem.quantity).label("total_sales")
        )
        .join(OrderItem, Dish.id == OrderItem.dish_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == "paid")
    )

    # Apply date filters to sales query
    if start_datetime:
        total_sales_query = total_sales_query.filter(Order.created_at >= start_datetime)

    if end_datetime:
        total_sales_query = total_sales_query.filter(Order.created_at <= end_datetime)

    total_sales_result = total_sales_query.first()
    total_sales = total_sales_result.total_sales if total_sales_result.total_sales else 0

    # Total customers (only count those who placed orders in the date range)
    if start_datetime or end_datetime:
        # Get unique person_ids from filtered orders
        person_subquery = orders_query.with_entities(Order.person_id).distinct().subquery()
        total_customers = db.query(Person).filter(Person.id.in_(person_subquery)).count()
    else:
        total_customers = db.query(Person).count()

    # Total orders
    total_orders = orders_query.count()

    # Total dishes
    total_dishes = db.query(Dish).count()

    # Average order value
    avg_order_value_query = (
        db.query(
            func.avg(
                db.query(func.sum(Dish.price * OrderItem.quantity))
                .join(OrderItem, Dish.id == OrderItem.dish_id)
                .filter(OrderItem.order_id == Order.id)
                .scalar_subquery()
            ).label("avg_order_value")
        )
        .filter(Order.status == "paid")
    )

    # Apply date filters to avg order value query
    if start_datetime:
        avg_order_value_query = avg_order_value_query.filter(Order.created_at >= start_datetime)

    if end_datetime:
        avg_order_value_query = avg_order_value_query.filter(Order.created_at <= end_datetime)

    avg_order_value_result = avg_order_value_query.first()
    avg_order_value = avg_order_value_result.avg_order_value if avg_order_value_result.avg_order_value else 0

    # Return all stats
    return {
        "total_sales": round(total_sales, 2),
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_dishes": total_dishes,
        "avg_order_value": round(avg_order_value, 2),
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }


# Get top customers by order count
@router.get("/top-customers")
def get_top_customers(request: Request, limit: int = 10, db: Session = Depends(get_db)):
    # Get customers with most orders
    top_customers_by_orders = (
        db.query(
            Person.id,
            Person.username,
            Person.visit_count,
            Person.last_visit,
            func.count(Order.id).label("order_count"),
            func.sum(
                db.query(func.sum(Dish.price * OrderItem.quantity))
                .join(OrderItem, Dish.id == OrderItem.dish_id)
                .filter(OrderItem.order_id == Order.id)
                .scalar_subquery()
            ).label("total_spent"),
        )
        .join(Order, Person.id == Order.person_id)
        .group_by(Person.id)
        .order_by(desc("order_count"))
        .limit(limit)
        .all()
    )

    # Format the results
    result = []
    for customer in top_customers_by_orders:
        result.append({
            "id": customer.id,
            "username": customer.username,
            "visit_count": customer.visit_count,
            "last_visit": customer.last_visit,
            "order_count": customer.order_count,
            "total_spent": round(customer.total_spent, 2) if customer.total_spent else 0,
            "avg_order_value": round(customer.total_spent / customer.order_count, 2) if customer.total_spent else 0,
        })

    return result


# Get top selling dishes
@router.get("/top-dishes")
def get_top_dishes(request: Request, limit: int = 10, db: Session = Depends(get_db)):
    # Get dishes with most orders
    top_dishes = (
        db.query(
            Dish.id,
            Dish.name,
            Dish.category,
            Dish.price,
            func.sum(OrderItem.quantity).label("total_ordered"),
            func.sum(Dish.price * OrderItem.quantity).label("total_revenue"),
        )
        .join(OrderItem, Dish.id == OrderItem.dish_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == "paid")
        .group_by(Dish.id)
        .order_by(desc("total_ordered"))
        .limit(limit)
        .all()
    )

    # Format the results
    result = []
    for dish in top_dishes:
        result.append({
            "id": dish.id,
            "name": dish.name,
            "category": dish.category,
            "price": dish.price,
            "total_ordered": dish.total_ordered,
            "total_revenue": round(dish.total_revenue, 2),
        })

    return result


# Get sales by category
@router.get("/sales-by-category")
def get_sales_by_category(request: Request, db: Session = Depends(get_db)):
    # Get sales by category
    sales_by_category = (
        db.query(
            Dish.category,
            func.sum(OrderItem.quantity).label("total_ordered"),
            func.sum(Dish.price * OrderItem.quantity).label("total_revenue"),
        )
        .join(OrderItem, Dish.id == OrderItem.dish_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == "paid")
        .group_by(Dish.category)
        .order_by(desc("total_revenue"))
        .all()
    )

    # Format the results
    result = []
    for category in sales_by_category:
        result.append({
            "category": category.category,
            "total_ordered": category.total_ordered,
            "total_revenue": round(category.total_revenue, 2),
        })

    return result


# Get sales over time (daily for the last 30 days)
@router.get("/sales-over-time")
def get_sales_over_time(request: Request, days: int = 30, db: Session = Depends(get_db)):
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Get sales by day
    sales_by_day = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("order_count"),
            func.sum(
                db.query(func.sum(Dish.price * OrderItem.quantity))
                .join(OrderItem, Dish.id == OrderItem.dish_id)
                .filter(OrderItem.order_id == Order.id)
                .scalar_subquery()
            ).label("total_sales"),
        )
        .filter(Order.status == "paid")
        .filter(Order.created_at >= start_date)
        .filter(Order.created_at <= end_date)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    # Create a dictionary with all dates in the range
    date_range = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        date_range[date_str] = {"order_count": 0, "total_sales": 0}
        current_date += timedelta(days=1)

    # Fill in the actual data
    for day in sales_by_day:
        date_str = day.date.strftime("%Y-%m-%d") if isinstance(day.date, datetime) else day.date
        date_range[date_str] = {
            "order_count": day.order_count,
            "total_sales": round(day.total_sales, 2) if day.total_sales else 0,
        }

    # Convert to list format
    result = []
    for date_str, data in date_range.items():
        result.append({
            "date": date_str,
            "order_count": data["order_count"],
            "total_sales": data["total_sales"],
        })

    return result


# Get chef performance metrics
@router.get("/chef-performance")
def get_chef_performance(request: Request, days: int = 30, db: Session = Depends(get_db)):
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Get completed orders count and average time to complete
    completed_orders = (
        db.query(Order)
        .filter(Order.status.in_(["completed", "paid"]))
        .filter(Order.created_at >= start_date)
        .filter(Order.created_at <= end_date)
        .all()
    )

    total_completed = len(completed_orders)

    # Calculate average items per order
    avg_items_per_order_query = (
        db.query(
            func.avg(
                db.query(func.count(OrderItem.id))
                .filter(OrderItem.order_id == Order.id)
                .scalar_subquery()
            ).label("avg_items")
        )
        .filter(Order.status.in_(["completed", "paid"]))
        .filter(Order.created_at >= start_date)
        .filter(Order.created_at <= end_date)
        .first()
    )

    avg_items_per_order = avg_items_per_order_query.avg_items if avg_items_per_order_query.avg_items else 0

    # Get busiest day of week
    busiest_day_query = (
        db.query(
            extract('dow', Order.created_at).label("day_of_week"),
            func.count(Order.id).label("order_count")
        )
        .filter(Order.created_at >= start_date)
        .filter(Order.created_at <= end_date)
        .group_by(extract('dow', Order.created_at))
        .order_by(desc("order_count"))
        .first()
    )

    busiest_day = None
    if busiest_day_query:
        # Convert day number to day name (0 = Sunday, 1 = Monday, etc.)
        day_names = list(calendar.day_name)
        day_number = int(busiest_day_query.day_of_week)
        busiest_day = day_names[day_number]

    return {
        "total_completed_orders": total_completed,
        "avg_items_per_order": round(avg_items_per_order, 2),
        "busiest_day": busiest_day,
    }


# Get table utilization statistics
@router.get("/table-utilization")
def get_table_utilization(request: Request, db: Session = Depends(get_db)):
    # Get all tables
    tables = db.query(Table).all()

    # Get order count by table
    table_orders = (
        db.query(
            Order.table_number,
            func.count(Order.id).label("order_count"),
            func.sum(
                db.query(func.sum(Dish.price * OrderItem.quantity))
                .join(OrderItem, Dish.id == OrderItem.dish_id)
                .filter(OrderItem.order_id == Order.id)
                .scalar_subquery()
            ).label("total_revenue"),
        )
        .group_by(Order.table_number)
        .all()
    )

    # Create a dictionary with all tables
    table_stats = {}
    for table in tables:
        table_stats[table.table_number] = {
            "table_number": table.table_number,
            "is_occupied": table.is_occupied,
            "order_count": 0,
            "total_revenue": 0,
        }

    # Fill in the actual data
    for table in table_orders:
        if table.table_number in table_stats:
            table_stats[table.table_number]["order_count"] = table.order_count
            table_stats[table.table_number]["total_revenue"] = round(table.total_revenue, 2) if table.total_revenue else 0

    # Convert to list format
    result = list(table_stats.values())

    # Sort by order count (descending)
    result.sort(key=lambda x: x["order_count"], reverse=True)

    return result


# Get customer visit frequency analysis
@router.get("/customer-frequency")
def get_customer_frequency(
    request: Request,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    # Parse date strings to datetime objects if provided
    start_datetime = None
    end_datetime = None

    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    # Get visit count distribution
    visit_counts_query = db.query(Person.visit_count)

    # Apply date filters if provided
    if start_datetime or end_datetime:
        # Get person IDs who placed orders in the date range
        orders_query = db.query(Order.person_id).distinct()

        if start_datetime:
            orders_query = orders_query.filter(Order.created_at >= start_datetime)

        if end_datetime:
            orders_query = orders_query.filter(Order.created_at <= end_datetime)

        person_ids = [result[0] for result in orders_query.all() if result[0] is not None]
        visit_counts_query = visit_counts_query.filter(Person.id.in_(person_ids))

    visit_counts = visit_counts_query.all()

    # Create frequency buckets
    frequency_buckets = {
        "1 visit": 0,
        "2-3 visits": 0,
        "4-5 visits": 0,
        "6-10 visits": 0,
        "11+ visits": 0,
    }

    # Fill the buckets
    for visit in visit_counts:
        count = visit.visit_count
        if count == 1:
            frequency_buckets["1 visit"] += 1
        elif 2 <= count <= 3:
            frequency_buckets["2-3 visits"] += 1
        elif 4 <= count <= 5:
            frequency_buckets["4-5 visits"] += 1
        elif 6 <= count <= 10:
            frequency_buckets["6-10 visits"] += 1
        else:
            frequency_buckets["11+ visits"] += 1

    # Convert to list format
    result = []
    for bucket, count in frequency_buckets.items():
        result.append({
            "frequency": bucket,
            "customer_count": count,
        })

    return result


# Get feedback analysis
@router.get("/feedback-analysis")
def get_feedback_analysis(
    request: Request,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    # Parse date strings to datetime objects if provided
    start_datetime = None
    end_datetime = None

    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    # Base query for feedback
    feedback_query = db.query(Feedback)

    # Apply date filters if provided
    if start_datetime:
        feedback_query = feedback_query.filter(Feedback.created_at >= start_datetime)

    if end_datetime:
        feedback_query = feedback_query.filter(Feedback.created_at <= end_datetime)

    # Get all feedback
    all_feedback = feedback_query.all()

    # Calculate average rating
    total_ratings = len(all_feedback)
    sum_ratings = sum(feedback.rating for feedback in all_feedback)
    avg_rating = round(sum_ratings / total_ratings, 1) if total_ratings > 0 else 0

    # Count ratings by score
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for feedback in all_feedback:
        rating_counts[feedback.rating] = rating_counts.get(feedback.rating, 0) + 1

    # Calculate rating percentages
    rating_percentages = {}
    for rating, count in rating_counts.items():
        rating_percentages[rating] = round((count / total_ratings) * 100, 1) if total_ratings > 0 else 0

    # Get recent feedback with comments
    recent_feedback = (
        db.query(Feedback, Person.username)
        .outerjoin(Person, Feedback.person_id == Person.id)
        .filter(Feedback.comment != None)
        .filter(Feedback.comment != "")
    )

    # Apply date filters if provided
    if start_datetime:
        recent_feedback = recent_feedback.filter(Feedback.created_at >= start_datetime)

    if end_datetime:
        recent_feedback = recent_feedback.filter(Feedback.created_at <= end_datetime)

    recent_feedback = recent_feedback.order_by(Feedback.created_at.desc()).limit(10).all()

    # Format recent feedback
    formatted_feedback = []
    for feedback, username in recent_feedback:
        formatted_feedback.append({
            "id": feedback.id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "username": username or "Anonymous",
            "created_at": feedback.created_at.isoformat(),
        })

    # Return analysis
    return {
        "total_feedback": total_ratings,
        "average_rating": avg_rating,
        "rating_counts": rating_counts,
        "rating_percentages": rating_percentages,
        "recent_comments": formatted_feedback,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }
