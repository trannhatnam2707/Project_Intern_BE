from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from Models.Users_Model import Users
from Schemas.User_Schemas import UserCreate, UserLogin
from Service.Auth_Service import  hash_password, verify_password
from Service.JWT_Service import create_access_token


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
    if not db_user or not verify_password(user.password, db_user.PasswordHash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng")
    
    token = create_access_token({"sub": db_user.Email,"role": db_user.Role})
    return {"access_token": token, "token_type": "bearer"}

#--------Lấy user hiện tại---------#
def get_current_user(db: Session, email: str):
    return db.query(Users).filter(Users.Email == email).first()

#--------
