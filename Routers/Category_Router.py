from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from Database.Connection import get_db
from Controllers.Category_Controller import get_all_categories
from Schemas.Categories_Schemas import CategoryOut

router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"]
)

@router.get("/", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)