# Schemas/Categories_Schemas.py
from pydantic import BaseModel

class CategoryBase(BaseModel):
    CategoryName: str

class CategoryOut(CategoryBase):
    CategoryID: int

    class Config:
        from_attributes = True