from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Controllers.Products_Controller import create_product, delete_product, get_all_products, get_product_by_id, update_product
from Database.Connection import get_db
from Models.Users_Model import Users
from Schemas.Products_Schemas import ProductCreate, ProductOut
from Utils.Dependencies import require_admin

router = APIRouter(
    prefix="/api/products",
    tags=["Products"],
)

# Create product (Only Admin)
@router.post("/", response_model=ProductOut)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(require_admin)
):
    return create_product(db, product)

# Get all products
@router.get("/", response_model=list[ProductOut])
def get_all(db: Session = Depends(get_db)):
    return get_all_products(db)

# Get product by ID
@router.get("/{product_id}", response_model=ProductOut)
def get_by_id(product_id: int, db: Session = Depends(get_db)):
    return get_product_by_id(db, product_id)

# Update product (Only Admin)
@router.put("/{product_id}", response_model=ProductOut)
def update_existing_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(require_admin)
):
    return update_product(db, product_id, data)

# Delete product (Only Admin)
@router.delete("/{product_id}")
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(require_admin)
):
    return delete_product(db, product_id)
