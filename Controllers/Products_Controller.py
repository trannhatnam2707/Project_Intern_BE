from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Products_Model import Product
from Schemas.Products_Schemas import ProductCreate


# --- Hàm giả lập gọi AI (Sau này bạn sẽ thay bằng gọi Gemini thật) ---
def generate_marketing_content_by_ai(product_name: str, description: str):
    # TODO: Sau này code gọi Gemini API sẽ nằm ở đây
    # prompt = f"Viết một câu marketing hấp dẫn cho sản phẩm {product_name} có đặc điểm {description}"
    # return gemini.generate(prompt)
    return f"🔥 SIÊU PHẨM {product_name} - {description} - MUA NGAY KẺO LỠ!"
    
# Create product
def create_product(db: Session, product_data: ProductCreate):
    new_product = Product(
        CategoryID=product_data.CategoryID,
        ProductName=product_data.ProductName,
        Price=product_data.Price,
        Description=product_data.Description,
        ImageURL=product_data.ImageURL,
        Stock=product_data.Stock,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Tạo sản phẩm thành công", "product": new_product}    

# Get all products
def get_all_products(db: Session):
    products = db.query(Product).all()
    return products

# Get product by ID
def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    return product

# Update product
def update_product(db: Session, product_id: int, data: ProductCreate):
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    for key, value in data.dict(exclude_unset=True).items():
        if hasattr(product, key):
            setattr(product, key, value)
    db.commit()
    db.refresh(product) 
    return {"message": "Cập nhật sản phẩm thành công", "product": product}

# Delete product
def delete_product(db: Session, product_id: int):   
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    db.delete(product)
    db.commit()
    return {"message": "Xóa sản phẩm thành công"}
