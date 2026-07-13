from fastapi import APIRouter, Depends, HTTPException                                           
from sqlalchemy.orm import Session                   
from app.database import get_db                                                                 
from app import models, auth                                                                    
from app.schemas import TodoCreate, TodoUpdate

router = APIRouter()
@router.post("/todos")
def post_todo(todo : TodoCreate, token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    new_todo = models.Todo(title=todo.title, description=todo.description,user_id = user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {"message" : "Todo added"}

@router.get("/get_todo")
def get_todo(token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todos = db.query(models.Todo).filter(models.Todo.user_id == user_id).all()
    return todos
    
@router.delete("/todos/{id}")
def delete_todo(id: int, token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todo = db.query(models.Todo).filter(models.Todo.user_id == user_id, models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not Found")
    db.delete(todo)
    db.commit()
    return {"message" : "Todo Deleted"}

@router.put("/todos/{id}")
def update_todo(id: int, new_todo: TodoUpdate, token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == user_id).first()
    todo.title = new_todo.title
    todo.description = new_todo.description
    db.commit()
    return {"message" : "Todo Updated Successfully"}