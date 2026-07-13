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
