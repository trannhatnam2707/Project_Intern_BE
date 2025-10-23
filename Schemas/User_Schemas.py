from datetime import datetime
from pydantic import BaseModel, EmailStr


#---------Request----------#

class UserCreate(BaseModel):
    FullName: str
    Email: EmailStr
    Password: str

class UserLogin(BaseModel):
    Email: EmailStr
    Password: str
    
#---------Response----------#
class UserOut(BaseModel):
    UserID: int
    FullName: str
    Email: EmailStr 
    Role: str
    CreatedAt: datetime

    class Config:
        from_attributes = True
    
    