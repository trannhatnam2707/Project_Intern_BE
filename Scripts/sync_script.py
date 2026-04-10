import sys
import os

# 1. Setup đường dẫn tuyệt đối (Để tránh lỗi ModuleNotFoundError)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from Database.Connection import SessionLocal

# ==============================================================================
# 👇 KHU VỰC IMPORT TOÀN BỘ MODEL (KITCHEN SINK APPROACH)
# Import hết tất cả các bảng để SQLAlchemy không còn báo thiếu quan hệ nữa.
# ==============================================================================

# 1. Các Model Cốt lõi (Chắc chắn có)
from Models.Users_Model import Users
from Models.Categories_Model import Category
from Models.Products_Model import Product
from Models.Order_Model import Order
from Models.OrderDetail_Model import OrderDetail
from Models.Reviews_Model import Reviews

# 2. Các Model Phụ (Thường gây lỗi thiếu quan hệ)
try:
    from Models.Payment_Model import Payment
except ImportError:
    print("⚠️ Không tìm thấy file Models/Payment_Model.py (Bỏ qua nếu không dùng)")

try:
    from Models.AdviceHistory_Model import AdviceHistory
except ImportError:
    try:
        from Models.AdviceHistory_Model import AdviceHistory
    except ImportError:
        pass # Bỏ qua

# try:
#     from Models.C import Cart
# except ImportError:
#     try:
#         from Models.Carts_Model import Cart
#     except ImportError:
#         pass # Bỏ qua

# ==============================================================================

from Service.Pinecone_Service import sync_product_to_pinecone
from Schemas.Pinecone_Schemas import ProductSyncData

def run_sync():
    print("🚀 Đang khởi động tiến trình đồng bộ dữ liệu lên Pinecone...")
    
    db = SessionLocal()
    
    try:
        # Lấy tất cả sản phẩm
        products = db.query(Product).all()
        total = len(products)
        
        if total == 0:
            print("⚠️ Database chưa có sản phẩm nào.")
            return

        print(f"📦 Tìm thấy {total} sản phẩm trong Database.")
        print("-" * 50)
        
        success_count = 0
        error_count = 0
        
        for index, p in enumerate(products):
            # In ra màn hình console
            print(f"🔄 [{index+1}/{total}] Đang xử lý: {p.ProductName}...", end=" ", flush=True)
            
            try:
                # Map dữ liệu
                data = ProductSyncData(
                    ProductID=p.ProductID,
                    ProductName=p.ProductName,
                    Description=p.Description or "",
                    Price=float(p.Price),
                    Stock=int(p.Stock),
                    ImageURL=p.ImageURL or "",
                    CategoryID=p.CategoryID
                )
                
                # Gọi Service (Action = UPSERT)
                result = sync_product_to_pinecone(
                    action="UPSERT", 
                    product_id=p.ProductID, 
                    data=data
                )
                
                if result:
                    print("✅") # In dấu tick xanh nếu xong
                    success_count += 1
                else:
                    print("❌")
                    error_count += 1
                    
            except Exception as e:
                print(f"\n❌ Lỗi ngoại lệ SP {p.ProductID}: {e}")
                error_count += 1

        print("\n" + "=" * 50)
        print(f"🎉 HOÀN TẤT ĐỒNG BỘ!")
        print(f"✅ Thành công: {success_count}")
        print(f"❌ Thất bại: {error_count}")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Lỗi kết nối/truy vấn Database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_sync()