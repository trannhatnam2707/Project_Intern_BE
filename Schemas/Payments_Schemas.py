import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from Models import Payment_Model

# ----- Request -----#
class PaymentCreate(BaseModel):
    OrderID: int
    Amount: Decimal
    PaymentMethod : Optional[str] = "Stripe"
    
    
# ----- Response -----#
class PaymentOut(BaseModel):
    PaymentID: int 
    OrderID: int    
    Amount: Decimal
    PaymentMethod: str
    PaymentStatus: str
    PaymentDate: datetime
    StripeSesseionID: Optional[str] = None
    
    class Config:
        from_attributes = True