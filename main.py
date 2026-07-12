from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
models.Base.metadata.create_all(bind = engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from pydantic import BaseModel

class UserCreate(BaseModel):
    name : str
    email : str
    password : str
    
class TodoCreate(BaseModel):
    description : str
    title : str

class TodoUpdate(BaseModel):
    description : str
    title : str

class UserLogin(BaseModel):
    email: str
    password: str



@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed=auth.hash_password(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message" : "Account created succesfully"}

@app.post("/login")                                                                             
def login(user: UserLogin, db: Session = Depends(get_db)):      
    db_user = db.query(models.User).filter(models.User.email == user.email).first()           
    if not db_user:                                                                             
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not auth.verify_password(user.password, db_user.password):                               
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = auth.create_token({"user_id": db_user.id})                                          
    return {"access_token": token}  

@app.post("/todos")
def post_todo(todo : TodoCreate, token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    new_todo = models.Todo(title=todo.title, description=todo.description,user_id = user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {"message" : "Todo added"}

@app.get("/get_todo")
def get_todo(token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todos = db.query(models.Todo).filter(models.Todo.user_id == user_id).all()
    return todos
    
@app.delete("/todos/{id}")
def delete_todo(id: int, token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todo = db.query(models.Todo).filter(models.Todo.user_id == user_id, models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not Found")
    db.delete(todo)
    db.commit()
    return {"message" : "Todo Deleted"}

@app.put("/todos/{id}")
def update_todo(id: int, new_todo: TodoUpdate, token: str, db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == user_id).first()
    todo.title = new_todo.title
    todo.description = new_todo.description
    db.commit()
    return {"message" : "Todo Updated Successfully"}
