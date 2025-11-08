from pydantic import BaseModel


class CategoryBase(BaseModel):
    CategoryName: str

class CategoryOut(CategoryBase):
    CategoryID: int

    class Config:
       class Config:
           from_attributes = True