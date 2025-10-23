from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine


#kết nối SQL server
DATABASE_URL = (
    "mssql+pyodbc://LAPTOP-9TFF98TE/EcommerceAI?"
    "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&UseFMTOnly=No"
)

# Tạo engine kết nối đến cơ sở dữ liệu
engine = create_engine(DATABASE_URL + "&MARS_Connection=Yes", connect_args={"autocommit": True, "unicode_results": True})

# ⚙️ Fix quan trọng: ép dùng NVARCHAR để lưu Unicode
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if isinstance(statement, str):
        statement = statement.replace("VARCHAR", "NVARCHAR")
    return statement, parameters

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