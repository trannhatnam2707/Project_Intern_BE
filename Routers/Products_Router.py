from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Controllers.Products_Controller import create_product, delete_product, get_all_products, get_product_by_id, update_product,generate_marketing_content_by_ai
from Database.Connection import get_db
from typing import Optional
from Models.Users_Model import Users
from Schemas.Products_Schemas import ProductCreate, ProductOut,ProductListResponse,GenerateContentRequest
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
@router.get("/", response_model=ProductListResponse) 
def get_all(
    category_id: Optional[int] = None,
    sort_by: Optional[str] = None,
    page: int = 1,
    limit: int = 12,
    search: Optional[str] = None, # Thêm tham số search
    db: Session = Depends(get_db)
):
    # Truyền search vào controller
    return get_all_products(db, category_id, sort_by, page, limit, search)

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


# API Sinh nội dung Marketing (Thêm vào router)
@router.post("/generate-marketing-content")
def generate_marketing(payload: GenerateContentRequest, db: Session = Depends(get_db)):
    content = generate_marketing_content_by_ai(payload.ProductName, payload.Description)
    return {"content": content}