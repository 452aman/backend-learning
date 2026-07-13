from fastapi import APIRouter, Depends, HTTPException                                           
from sqlalchemy.orm import Session                                                                                                                     
from app import models, auth                                    
from app.schemas import UserCreate, UserLogin 
from app.database import get_db   
router = APIRouter()

@router.post("/signup")
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

@router.post("/login")                                                                             
def login(user: UserLogin, db: Session = Depends(get_db)):      
    db_user = db.query(models.User).filter(models.User.email == user.email).first()           
    if not db_user:                                                                             
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not auth.verify_password(user.password, db_user.password):                               
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = auth.create_token({"user_id": db_user.id})                                          
    return {"access_token": token}  
