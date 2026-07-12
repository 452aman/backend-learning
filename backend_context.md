# Backend Learning Context

## Project Location
/Users/amanparmar/Desktop/backend_learning

## Run Command
```bash
cd /Users/amanparmar/Desktop/backend_learning
source backend_learning_env/bin/activate
backend_learning_env/bin/python3 -m uvicorn main:app --reload
```

## Test API
http://localhost:8000/docs

---

## Stack
- Language: Python
- Framework: FastAPI
- Database: SQLite (file: database.db)
- ORM: SQLAlchemy
- Auth: JWT (python-jose) + bcrypt (passlib)

## requirements.txt
```
fastapi
uvicorn
sqlalchemy
python-jose
passlib
bcrypt==4.0.1
python-multipart
```

---

## Project Structure
```
backend_learning/
├── main.py          → API routes
├── database.py      → DB connection setup
├── models.py        → Table definitions (User + Todo)
├── auth.py          → Password hashing + JWT
├── database.db      → Actual SQLite database file
└── backend_context.md
```

---

## File: database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
```

---

## File: models.py
```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
```

---

## File: auth.py
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

---

## File: main.py
```python
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class TodoCreate(BaseModel):
    description: str
    title: str

class TodoUpdate(BaseModel):
    description: str
    title: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Account created successfully"}

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
def post_todo(todo: TodoCreate, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    new_todo = models.Todo(title=todo.title, description=todo.description, user_id=user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {"message": "Todo added"}

@app.get("/get_todo")
def get_todo(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todos = db.query(models.Todo).filter(models.Todo.user_id == user_id).all()
    return todos

@app.delete("/todos/{id}")
def delete_todo(id: int, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todo = db.query(models.Todo).filter(models.Todo.user_id == user_id, models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not Found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo Deleted"}

@app.put("/todos/{id}")
def update_todo(id: int, new_todo: TodoUpdate, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = auth.verify_token(token)
    user_id = payload.get("user_id")
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == user_id).first()
    todo.title = new_todo.title
    todo.description = new_todo.description
    db.commit()
    return {"message": "Todo Updated Successfully"}
```

---

## Key Concepts

### HTTP Methods
- GET    → fetch data
- POST   → send/create data
- PUT    → update data
- DELETE → delete data

### DB Patterns (memorize these 4)
```python
db.query(Model).all()                          # fetch all
db.query(Model).filter(Model.id == id).first() # fetch one
db.add(item); db.commit()                      # save new
db.delete(item); db.commit()                   # delete
```

### Auth Flow
```
SIGNUP:  hash password → save to DB
LOGIN:   verify password → create JWT token → return token
PROTECTED ROUTE: read Authorization header → strip "Bearer " → verify token → get user_id
```

### Filter with multiple conditions
```python
db.query(Model).filter(Model.field1 == val1, Model.field2 == val2).first()
# use comma, NOT 'and'
```

### Error Handling
```python
raise HTTPException(status_code=400, detail="message")
# 400 = bad request
# 404 = not found
# 401 = unauthorized
```

---

## What's Been Built
- POST /signup        → create account (with hashed password)
- POST /login         → login and get JWT token
- POST /todos         → create todo (Bearer token in header)
- GET  /get_todo      → get all my todos (Bearer token in header)
- PUT  /todos/{id}    → update a todo (Bearer token in header)
- DELETE /todos/{id}  → delete a todo (Bearer token in header)

## What's Next
- Fix curl 422 issue on login (investigate)
- Alembic migrations (replace create_all)
- Switch SQLite → PostgreSQL
- Deployment on Render/Railway
