from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    FullName: str
    Email: EmailStr

#---------Request----------#

class UserCreate(UserBase):
    Password: str

class UserLogin(BaseModel):
    Email: EmailStr
    Password: str
    
    
#-----Update User-------#
class UserUpdate(BaseModel):
    FullName: Optional[str] = None
    Password: Optional[str] = None
    
class ChangePassword(BaseModel):
    OldPassword: str
    NewPassword: str

#---------Response----------#
class UserOut(BaseModel):
    UserID: int
    FullName: str
    Email: EmailStr 
    Role: str
    CreatedAt: datetime

    class Config:
        from_attributes = True

