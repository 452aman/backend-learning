# Backend Learning Context

## Project Location
/Users/amanparmar/Desktop/backend_learning

## GitHub Repo
https://github.com/452aman/backend-learning

## Live URL
https://backend-learning-0l5e.onrender.com/docs

## Run Locally
```bash
cd /Users/amanparmar/Desktop/backend_learning
source backend_learning_env/bin/activate
backend_learning_env/bin/python3 -m uvicorn main:app --reload
```

---

## Stack
- Language: Python
- Framework: FastAPI
- Database: PostgreSQL (local + Render)
- ORM: SQLAlchemy
- Migrations: Alembic
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
alembic
psycopg2-binary
```

---

## Project Structure
```
backend_learning/
├── main.py              → API routes
├── database.py          → DB connection setup
├── models.py            → Table definitions (User + Todo)
├── auth.py              → Password hashing + JWT
├── alembic/             → Migration files
├── alembic.ini          → Alembic config
├── requirements.txt
└── backend_context.md
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
PROTECTED ROUTE: read token → verify → get user_id → fetch data
```

### Filter with multiple conditions
```python
db.query(Model).filter(Model.field1 == val1, Model.field2 == val2).first()
# use comma, NOT 'and'
```

### Alembic workflow
```
Change models.py
→ alembic revision --autogenerate -m "description"
→ alembic upgrade head
```

### Error Handling
```python
raise HTTPException(status_code=400, detail="message")
# 400 = bad request  |  404 = not found  |  401 = unauthorized
```

### Debugging steps
```
1. Look at the request URL    → what was sent wrong?
2. Find YOUR file in traceback → where did it break?
3. Read the last line          → what exactly broke?
```

---

## What's Been Built
- POST /signup        → create account (hashed password)
- POST /login         → get JWT token
- POST /todos         → create todo (token auth)
- GET  /get_todo      → get all my todos (token auth)
- PUT  /todos/{id}    → update a todo (token auth)
- DELETE /todos/{id}  → delete a todo (token auth)

## What's Next
- Docker (containerize the app)
- Proper OAuth2 Bearer token with Swagger support
- Background tasks
- Redis caching
