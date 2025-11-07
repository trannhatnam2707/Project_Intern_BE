from dotenv import load_dotenv
from fastapi import HTTPException 
from sqlalchemy.orm import Session
from Models.Users_Model import Users
import os
from Service.Auth_Service import hash_password, verify_password
from Service.JWT_Service import create_access_token, create_refresh_token

load_dotenv()
ADMIN_SETUP_KEY = os.getenv("ADMIN_SETUP_KEY")  

#---------------create admin account ----------------#
def create_admin(db:Session, full_name: str, email: str, password: str, setup_key: str):
    #check key setup
    if setup_key != ADMIN_SETUP_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin setup key")
    
    #kiểm tra email đã tồn tại
    existing_admin = db.query(Users).filter(Users.Email == email, Users.Role == "admin").first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin account with this email already exists")
    
    # 🔐 Tạo mật khẩu mã hóa
    hashed_pw = hash_password(password)
    
    new_admin = Users(
        FullName=full_name,
        Email=email,
        Password=hashed_pw,
        Role="admin"
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin account created successfully", "email": new_admin.Email, "role": new_admin.Role}

# ------------------- ADMIN: Lấy danh sách user -------------------
def get_all_users(db: Session):
    users = db.query(Users).all()
    return users

# ------------------- ADMIN: Xem chi tiết user -------------------
def get_user_by_id(db: Session, user_id: int):
    user = db.query(Users).filter(Users.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user


# ------------------- ADMIN: Đổi quyền -------------------
def update_user_role(db: Session, user_id: int, new_role: str):
    user = db.query(Users).filter(Users.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    user.Role = new_role
    db.commit()
    return {"message": f"Đã cập nhật quyền người dùng {user.Email} thành {new_role}"}


# ------------------- ADMIN: Xoá tài khoản -------------------
def delete_user(db: Session, user_id: int):
    user = db.query(Users).filter(Users.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    db.delete(user)
    db.commit()
    return {"message": "Xóa tài khoản thành công"}
    
# ---- Xoá tất cả người dùng ---- #
def delete_all_users(db: Session):
    users = db.query(Users).filter(Users.Role != "admin").all()
    if not users:
        raise HTTPException(status_code=404, detail="Không có người dùng để xóa")
    
    for user in users:
        db.delete(user)
    db.commit()
    return {"message": f"Đã xóa toàn bộ {len(users)} người dùng ngoại trừ admin"}