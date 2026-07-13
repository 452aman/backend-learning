from fastapi import FastAPI
from app.database import engine
from app import models
from app.routes import auth, todos

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
