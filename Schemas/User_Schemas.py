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
    PhoneNumber: Optional[str] = None
    Address: Optional[str] = None
    
class ChangePassword(BaseModel):
    OldPassword: str
    NewPassword: str

#---------Reset Password Request----------#    
class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

#---------Response----------#
class UserOut(BaseModel):
    UserID: int
    FullName: str
    Email: EmailStr 
    Role: str
    CreatedAt: datetime
    PhoneNumber: Optional[str] = None
    Address: Optional[str] = None

    class Config:
        from_attributes = True

