from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import Table as TableModel, Order, get_session_db
from ..models.table import Table, TableCreate, TableUpdate, TableStatus
from ..middleware import get_session_id

router = APIRouter(
    prefix="/tables",
    tags=["tables"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get session-aware database
def get_session_database(request: Request):
    session_id = get_session_id(request)
    return next(get_session_db(session_id))


# Get all tables
@router.get("/", response_model=List[Table])
def get_all_tables(request: Request, db: Session = Depends(get_session_database)):
    return db.query(TableModel).order_by(TableModel.table_number).all()


# Get table by ID
@router.get("/{table_id}", response_model=Table)
def get_table(table_id: int, request: Request, db: Session = Depends(get_session_database)):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table


# Get table by table number
@router.get("/number/{table_number}", response_model=Table)
def get_table_by_number(table_number: int, request: Request, db: Session = Depends(get_session_database)):
    db_table = (
        db.query(TableModel).filter(TableModel.table_number == table_number).first()
    )
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table


# Create new table
@router.post("/", response_model=Table)
def create_table(table: TableCreate, request: Request, db: Session = Depends(get_session_database)):
    # Check if a table with this number already exists
    existing_table = (
        db.query(TableModel)
        .filter(TableModel.table_number == table.table_number)
        .first()
    )
    if existing_table:
        raise HTTPException(
            status_code=400,
            detail=f"Table with number {table.table_number} already exists",
        )

    # Create new table
    db_table = TableModel(
        table_number=table.table_number,
        is_occupied=table.is_occupied,
        current_order_id=table.current_order_id,
        last_occupied_at=table.last_occupied_at,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table


# Update table
@router.put("/{table_id}", response_model=Table)
def update_table(
    table_id: int, table_update: TableUpdate, request: Request, db: Session = Depends(get_session_database)
):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Update fields if provided
    if table_update.is_occupied is not None:
        db_table.is_occupied = table_update.is_occupied
    if table_update.current_order_id is not None:
        db_table.current_order_id = table_update.current_order_id

    db_table.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_table)
    return db_table


# Delete table
@router.delete("/{table_id}")
def delete_table(table_id: int, request: Request, db: Session = Depends(get_session_database)):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Check if table is currently occupied
    if db_table.is_occupied:
        raise HTTPException(
            status_code=400, detail="Cannot delete a table that is currently occupied"
        )

    db.delete(db_table)
    db.commit()
    return {"message": "Table deleted successfully"}


# Get table status (total, occupied, free)
@router.get("/status/summary", response_model=TableStatus)
def get_table_status(request: Request, db: Session = Depends(get_session_database)):
    total_tables = db.query(TableModel).count()
    occupied_tables = (
        db.query(TableModel).filter(TableModel.is_occupied == True).count()
    )
    free_tables = total_tables - occupied_tables

    return {
        "total_tables": total_tables,
        "occupied_tables": occupied_tables,
        "free_tables": free_tables,
    }


# Set table as occupied
@router.put("/{table_id}/occupy", response_model=Table)
def set_table_occupied(
    table_id: int, order_id: int = None, request: Request = None, db: Session = Depends(get_session_database)
):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Check if table is already occupied
    if db_table.is_occupied:
        raise HTTPException(status_code=400, detail="Table is already occupied")

    # Update table status
    db_table.is_occupied = True

    # Link to order if provided
    if order_id:
        # Verify order exists
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        db_table.current_order_id = order_id

    db_table.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_table)
    return db_table


# Set table as free
@router.put("/{table_id}/free", response_model=Table)
def set_table_free(table_id: int, request: Request, db: Session = Depends(get_session_database)):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Check if table is already free
    if not db_table.is_occupied:
        raise HTTPException(status_code=400, detail="Table is already free")

    # Update table status
    db_table.is_occupied = False
    db_table.current_order_id = None
    db_table.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_table)
    return db_table


# Set table as occupied by table number
@router.put("/number/{table_number}/occupy", response_model=Table)
def set_table_occupied_by_number(table_number: int, request: Request, db: Session = Depends(get_session_database)):
    db_table = (
        db.query(TableModel).filter(TableModel.table_number == table_number).first()
    )
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Update table status (even if already occupied, just update the timestamp)
    db_table.is_occupied = True
    db_table.last_occupied_at = datetime.now(timezone.utc)
    db_table.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_table)
    return db_table


# Set table as free by table number
@router.put("/number/{table_number}/free", response_model=Table)
def set_table_free_by_number(table_number: int, request: Request, db: Session = Depends(get_session_database)):
    db_table = (
        db.query(TableModel).filter(TableModel.table_number == table_number).first()
    )
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Update table status to free (don't check if already free, just update)
    db_table.is_occupied = False
    db_table.current_order_id = None
    db_table.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_table)
    return db_table


# Create multiple tables at once
@router.post("/batch", response_model=List[Table])
def create_tables_batch(num_tables: int, request: Request, db: Session = Depends(get_session_database)):
    if num_tables <= 0:
        raise HTTPException(
            status_code=400, detail="Number of tables must be greater than 0"
        )

    # Get the highest existing table number
    highest_table = (
        db.query(TableModel).order_by(TableModel.table_number.desc()).first()
    )
    start_number = 1
    if highest_table:
        start_number = highest_table.table_number + 1

    # Create tables
    new_tables = []
    for i in range(start_number, start_number + num_tables):
        db_table = TableModel(
            table_number=i,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(db_table)
        new_tables.append(db_table)

    db.commit()

    # Refresh all tables
    for table in new_tables:
        db.refresh(table)

    return new_tables
