from datetime import timedelta
from turtle import reset
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from Models.Users_Model import Users
from Schemas.User_Schemas import ResetPasswordConfirm, UserCreate, UserLogin, UserUpdate, ChangePassword
from Service.Auth_Service import  hash_password, verify_password
from Service.Email_Service import send_reset_password_email
from Service.JWT_Service import create_access_token, create_refresh_token, verify_refresh_token, verify_reset_token
import os
from dotenv import load_dotenv  

load_dotenv()
ADMIN_SETUP_KEY = os.getenv("ADMIN_SETUP_KEY")  

#------Đăng ký người dùng-------#
def register_user(db: Session,user: UserCreate):
    
    if db.query(Users).filter(Users.Email == user.Email).first():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    
    hashed_pw = hash_password(user.Password)
    new_user = Users(
        FullName = user.FullName,
        Email = user.Email, 
        Password = hashed_pw 
    )
 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {new_user, "Đăng ký thành công"}

#--------Đăng nhập--------------#
def login_user(db:Session , user: UserLogin):
    db_user = db.query(Users).filter(Users.Email == user.Email).first()
    if not db_user or not verify_password(user.Password, db_user.Password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng")
    
    #sinh token chung cho cả user và admin
    access_token = create_access_token({"sub": db_user.Email,"role": db_user.Role})
    refresh_token = create_refresh_token({"sub": db_user.Email,"role": db_user.Role})

    return {
        "message": "Đăng nhập thành công",
        "user": {
            "user_id": db_user.UserID,
            "full_name": db_user.FullName,
            "email": db_user.Email,
            "role": db_user.Role
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    
    
# ========== ADMIN PHẦN GỘP ==========
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


# ------------------- Lấy thông tin người dùng hiện tại -------------------
def get_me(db: Session, current_user: Users):
    return {
        "UserID": current_user.UserID,
        "FullName": current_user.FullName,
        "Email": current_user.Email,
        "Role": current_user.Role,
        "CreatedAt": current_user.CreatedAt
    }

#--------Cập nhật thông tin người dùng-------#
def update_profile(db: Session, current_user: Users, update_data: UserUpdate):
    db_user = db.query(Users).filter(Users.UserID == current_user.UserID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    db_user.FullName = update_data.FullName or db_user.FullName
    db.commit()
    db.refresh(db_user) 
    return {"message": "Cập nhật thông tin thành công"}

#----------Đổi mật khẩu người dùng--------#
def change_password(db: Session, current_user: Users, data: ChangePassword):
    db_user = db.query(Users).filter(Users.UserID == current_user.UserID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    if not verify_password(data.old_password, db_user.PasswordHash):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng")

    db_user.PasswordHash = hash_password(data.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}

#--------Refresh token-------#
def refresh_access_token(refresh_token: str):
    payload = verify_refresh_token(refresh_token)
    email = payload.get("sub")
    
    if not email:
        raise HTTPException(status_code=400, detail="Refresh Token không hợp lệ")
    
    new_access_token = create_access_token({"sub": email})
    return {"access_token": new_access_token, "token_type": "bearer"}

#-------Quên mật khẩu (Gửi mail)-------#
async def forgot_password(db: Session, email: str, background_tasks: BackgroundTasks):
    # 1. Kiểm tra email có tồn tại không
    user = db.query(Users).filter(Users.Email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại trong hệ thống")

    # 2. Tạo Token reset (hết hạn sau 15 phút)
    # Token này chứa email của user để lát nữa xác thực
    reset_token = create_access_token(
        data={"sub": user.Email, "type": "reset"}, 
        expires_delta=timedelta(minutes=15)
    )

    # 3. Gửi email (Dùng BackgroundTasks để API không bị đơ khi đang gửi mail)
    background_tasks.add_task(send_reset_password_email, user.Email, reset_token)

    return {"message": "Đã gửi hướng dẫn khôi phục mật khẩu. Vui lòng kiểm tra email!"}

def confirm_reset_password(db: Session, data: ResetPasswordConfirm):
    # 1. Xác thực token
    payload = verify_reset_token(data.token)
    email = payload.get("sub")
     
    if not email:
        raise HTTPException(status_code=400, detail="Reset Token không hợp lệ")
    
    # 2. Tìm user theo email
    user = db.query(Users).filter(Users.Email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    # 3. Cập nhật mật khẩu mới
    user.Password = hash_password(data.new_password)
    db.commit()
    
    return {"message": "Đặt lại mật khẩu thành công"}
