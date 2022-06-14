import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, APIRouter
import models  # the python file with tables and columns
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={401: {"todo": "Not Found"}}
)


models.Base.metadata.create_all(bind=engine)


def get_db():
    """
    Create a database session
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(lt=6, gt=0, description="Should be between 1-5")
    complete: bool


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    """
    Returns all the todos
    """
    return db.query(models.Todos).all()


@router.get("/user")
async def read_all_by_user(user: object = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """
    Returns the todos associated with the user
    """
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.id).all()


@router.get("/{todo_id}")
async def read_todo(todo_id: int, user: object = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns based on todo_id and the user
    """
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).\
        filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise http_exception()


@router.post("/")
async def create_todo(todo: Todo, user: object = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.id
    db.add(todo_model)
    db.commit()
    response = {
        "status": True
    }
    return response


@router.put("/{todo_id}")
async def update_todo(todo_id: int,
                      todo: Todo,
                      user: object = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    Method for updating todos
    """
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).\
        filter(models.Todos.owner_id == user.id).first()
    if todo_model is None:
        return http_exception()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.add(todo_model)
    db.commit()
    return successful_message(201)


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int,
                      user: object = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    Method for deleting todos
    """
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).\
        filter(models.Todos.owner_id == user.id).first()
    if todo_model is None:
        return http_exception()
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return successful_message(201)


def http_exception():
    return HTTPException(status_code=404, detail="Todo id not found in database")


def successful_message(status_code: int):
    return {"Status code": status_code, "transaction": "Successful"}

