from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_ # Import thêm or_
from Models.Products_Model import Product
from Models.Categories_Model import Category # Import thêm Category
from Schemas.Products_Schemas import ProductCreate
import google.generativeai as genai
from Schemas.Pinecone_Schemas import ProductSyncData
from Service.Pinecone_Service import sync_product_to_pinecone
import os
from dotenv import load_dotenv


load_dotenv()

GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

def generate_marketing_content_by_ai(product_name: str, description: str):
    if not GENAI_API_KEY:
        return "Chưa cấu hình GEMINI_API_KEY trong Backend!"
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash') # Hoặc gemini-1.5-flash
        
        prompt = f"""
        Bạn là chuyên gia marketing trong lĩnh vực công nghệ. 
Hãy tạo nội dung quảng cáo ngắn gọn và hấp dẫn cho một sản phẩm điện tử.

🎯 **Yêu cầu nội dung:**
- Viết bằng tiếng Việt.
- Độ dài: 4–5 câu.
- Giọng văn: sinh động, thu hút, mang cảm giác chuyên nghiệp.
- Có sử dụng emoji nhưng không lạm dụng (2–4 emoji).
- Nhấn mạnh lợi ích, trải nghiệm người dùng và điểm nổi bật của sản phẩm.
- Cuối đoạn có lời kêu gọi hành động (CTA) nhẹ nhàng.
- Không được tự bịa đặt thông số kỹ thuật không có trong dữ liệu đầu vào.
- Mỗi sản phẩm là câu marketing phải khác nhau
- Chỉ cần gen ra đoạn marketing thôi, không cần phải "chào bạn, tôi sẽ tạo ,..." .


📦 **Thông tin sản phẩm:**
- Tên sản phẩm: {product_name}
- Mô tả / Đặc điểm nổi bật: {description if description else "Sản phẩm công nghệ đời mới với nhiều tính năng hiện đại."}

Hãy viết nội dung sao cho phù hợp quảng cáo Facebook hoặc website bán hàng.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi AI: {str(e)}"


# Create product
def create_product(db: Session, product_data: ProductCreate):
    new_product = Product(
        CategoryID=product_data.CategoryID,
        ProductName=product_data.ProductName,
        Price=product_data.Price,
        Description=product_data.Description,
        MarketingContent=product_data.MarketingContent, 
        ImageURL=product_data.ImageURL,
        Stock=product_data.Stock,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # 👇 ĐỒNG BỘ PINECONE
    try:
        sync_data = ProductSyncData(
            ProductID=new_product.ProductID,
            ProductName=new_product.ProductName,
            Description=new_product.Description,
            Price=new_product.Price,
            Stock=new_product.Stock,
            ImageURL=new_product.ImageURL
        )
        sync_product_to_pinecone(action="UPSERT", product_id=new_product.ProductID, data=sync_data)
    except Exception as e:
        print(f"Lỗi Sync Pinecone: {e}")

    return new_product

# Get all products
def get_all_products(db: Session, category_id: int = None, sort_by: str = None, page: int = 1, limit: int = 6, search: str = None):
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

     # 👇 ĐỒNG BỘ PINECONE
    try:
        sync_data = ProductSyncData(
            ProductID=product.ProductID,
            ProductName=product.ProductName,
            Description=product.Description,
            Price=product.Price,
            Stock=product.Stock,
            ImageURL=product.ImageURL
        )
        sync_product_to_pinecone(action="UPSERT", product_id=product.ProductID, data=sync_data)
    except Exception as e:
        print(f"Lỗi Sync Pinecone: {e}")

    return product

# Delete product
def delete_product(db: Session, product_id: int):   
    product = db.query(Product).filter(Product.ProductID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    db.delete(product)
    db.commit()
    # 👇 ĐỒNG BỘ PINECONE (XÓA)
    try:
        sync_product_to_pinecone(action="DELETE", product_id=product_id)
    except Exception as e:
        print(f"Lỗi Sync Pinecone: {e}")
        
    return {"message": "Xóa thành công"}
