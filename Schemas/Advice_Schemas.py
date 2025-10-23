from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from Models.Users_Model import User 


#----- Request -----#
class AdviceCreate(BaseModel):
    UserID: Optional[int] = None
    UserQuery: str

#----- Response -----#
class AdviceResponse(BaseModel):
    AdviceID: int
    UserID: Optional[int] 
    UserQuery: str  
    AIResponse: str
    CreatedAt: datetime
    
    class Config:
        from_attributes = True