from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_ # Import thêm or_
from Models.Products_Model import Product
from Models.Categories_Model import Category # Import thêm Category
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
def get_all_products(db: Session, category_id: int = None, sort_by: str = None, page: int = 1, limit: int = 12, search: str = None):
    # Join bảng Category để tìm kiếm theo tên danh mục
    query = db.query(Product).join(Category, Product.CategoryID == Category.CategoryID)
    
    # 1. Lọc theo danh mục (nếu chọn menu)
    if category_id:
        query = query.filter(Product.CategoryID == category_id)

    # 2. 👇 LOGIC TÌM KIẾM MỞ RỘNG (Name OR Description OR CategoryName)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.ProductName.like(search_pattern),       # Tìm trong tên
                Product.Description.like(search_pattern),       # Tìm trong mô tả
                Category.CategoryName.like(search_pattern)      # Tìm trong tên danh mục (ví dụ "Đồng hồ")
            )
        )
    
    # 3. Sắp xếp
    if sort_by == 'newest':
        query = query.order_by(desc(Product.ProductID))
    elif sort_by == 'best_seller':
        query = query.order_by(desc(Product.Sold))
    elif sort_by == 'price_asc':
        query = query.order_by(Product.Price)
    elif sort_by == 'price_desc':
        query = query.order_by(desc(Product.Price))
    else:
        query = query.order_by(Product.ProductID) 
        
    # 4. Tính tổng và Phân trang
    total_records = query.count()
    skip = (page - 1) * limit
    products = query.offset(skip).limit(limit).all()
    
    return {
        "data": products,
        "total": total_records,
        "page": page,
        "limit": limit
    }

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
