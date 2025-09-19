from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import cast
from sqlalchemy.types import Date
from typing import List, Optional
from datetime import datetime, date
import json

from models import (
    Todo, get_db, create_tables, 
    TodoCreate, TodoUpdate, TodoResponse,
    Priority, Status
)

# Create FastAPI app
app = FastAPI(
    title="Advanced Todo API",
    description="A comprehensive todo management system",
    version="1.0.0"
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Helper functions
def get_todo_or_404(todo_id: int, db: Session):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

def update_todo_status_timestamps(todo: Todo, new_status: str):
    if new_status == Status.COMPLETED.value and todo.status != Status.COMPLETED.value:
        todo.completed_at = datetime.utcnow()
    elif new_status != Status.COMPLETED.value:
        todo.completed_at = None

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Advanced Todo API is running!", "version": "1.0.0"}

@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo.to_dict()

@app.get("/todos/", response_model=List[TodoResponse])
def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern="^(pending|in_progress|completed|cancelled)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|urgent)$"),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Todo)
    
    if status:
        query = query.filter(Todo.status == status)
    if priority:
        query = query.filter(Todo.priority == priority)
    if category:
        query = query.filter(Todo.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            Todo.title.ilike(f"%{search}%") | 
            Todo.description.ilike(f"%{search}%")
        )
    
    query = query.order_by(Todo.created_at.desc())
    todos = query.offset(skip).limit(limit).all()
    return [todo.to_dict() for todo in todos]

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo_or_404(todo_id, db)
    return todo.to_dict()

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    todo = get_todo_or_404(todo_id, db)
    
    update_data = todo_update.dict(exclude_unset=True)
    
    if "status" in update_data:
        update_todo_status_timestamps(todo, update_data["status"])
    
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo.to_dict()

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo_or_404(todo_id, db)
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.patch("/todos/{todo_id}/status")
def update_todo_status(
    todo_id: int, 
    status: str = Query(..., pattern="^(pending|in_progress|completed|cancelled)$"),
    db: Session = Depends(get_db)
):
    todo = get_todo_or_404(todo_id, db)
    update_todo_status_timestamps(todo, status)
    todo.status = status
    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo.to_dict()

@app.get("/todos/stats/summary")
def get_todo_stats(db: Session = Depends(get_db)):
    total = db.query(Todo).count()
    pending = db.query(Todo).filter(Todo.status == Status.PENDING.value).count()
    in_progress = db.query(Todo).filter(Todo.status == Status.IN_PROGRESS.value).count()
    completed = db.query(Todo).filter(Todo.status == Status.COMPLETED.value).count()
    cancelled = db.query(Todo).filter(Todo.status == Status.CANCELLED.value).count()
    
    urgent = db.query(Todo).filter(Todo.priority == Priority.URGENT.value).count()
    high = db.query(Todo).filter(Todo.priority == Priority.HIGH.value).count()
    medium = db.query(Todo).filter(Todo.priority == Priority.MEDIUM.value).count()
    low = db.query(Todo).filter(Todo.priority == Priority.LOW.value).count()
    
    overdue = db.query(Todo).filter(
        Todo.due_date < datetime.utcnow(),
        Todo.status != Status.COMPLETED.value
    ).count()
    
    return {
        "total": total,
        "status": {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled
        },
        "priority": {
            "urgent": urgent,
            "high": high,
            "medium": medium,
            "low": low
        },
        "overdue": overdue,
        "completion_rate": round((completed / total * 100), 2) if total > 0 else 0
    }

@app.get("/todos/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Todo.category).distinct().filter(Todo.category.isnot(None)).all()
    return [cat[0] for cat in categories if cat[0]]

@app.get("/todos/overdue/")
def get_overdue_todos(db: Session = Depends(get_db)):
    overdue_todos = db.query(Todo).filter(
        Todo.due_date < datetime.utcnow(),
        Todo.status != Status.COMPLETED.value
    ).order_by(Todo.due_date.asc()).all()
    return [todo.to_dict() for todo in overdue_todos]

@app.get("/todos/due-today/")
def get_due_today_todos(db: Session = Depends(get_db)):
    from datetime import date
    today = date.today()
    due_today = db.query(Todo).filter(
        cast(Todo.due_date, Date) == today,
        Todo.status != Status.COMPLETED.value
    ).all()
    return [todo.to_dict() for todo in due_today]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)