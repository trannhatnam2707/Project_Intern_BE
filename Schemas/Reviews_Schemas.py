from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    Rating: int
    Comment: Optional[str] = None

class ReviewOut(BaseModel):
    ReviewID: int
    UserID: int
    FullName: str  # Tên người đánh giá (lấy từ bảng User)
    Rating: int
    Comment: Optional[str]
    CreatedAt: datetime

    class Config:
        from_attributes = True