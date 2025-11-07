
from hmac import new
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from Models.Users_Model import Users
from Schemas.User_Schemas import UserCreate, UserLogin, UserUpdate, ChangePassword
from Service.Auth_Service import  hash_password, verify_password
from Service.JWT_Service import create_access_token, create_refresh_token, verify_refresh_token


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

