from sqlalchemy.orm import Session
from Models.Categories_Model import Category

def get_all_categories(db: Session):
    return db.query(Category).all()