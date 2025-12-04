from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine


#kết nối SQL server
DATABASE_URL = (
    "mssql+pyodbc://LAPTOP-9TFF98TE/EcommerceAI"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&charset=utf8"
)

# Tạo engine kết nối đến cơ sở dữ liệu
engine = create_engine(
    DATABASE_URL,
    fast_executemany=True,
    connect_args={
        "unicode_results": True,
    }
)

# Tạo session (kết nối logic để thao tác CRUD)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base để kế thừa cho các model
Base = declarative_base()

def get_db():
    """Hàm tạo và đóng session kết nối đến cơ sở dữ liệu."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def test_connection():
    """Hàm kiểm tra kết nối đến cơ sở dữ liệu."""
    try:
        with engine.connect() as connection:
            print("Kết nối đến cơ sở dữ liệu thành công!")
    except Exception as e:
        print("Kết nối đến cơ sở dữ liệu thất bại:", e)
        
test_connection()