from fastapi import HTTPException, status
from Database.Connection import engine
from sqlalchemy.orm import sessionmaker
from Models.Users_Model import Users
from Schemas.User_Schemas import UserCreate, UserLogin
from Service.Auth_Service import create_access_token, hash_password, verify_password 

SessionLocal = sessionmaker(bind=engine)

#------Đăng ký người dùng-------#
def register_user(user: UserCreate):
    db = SessionLocal()
    exitsting_user = db.query(Users).filter(Users.Email == user.Email).first()
    if exitsting_user:
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
    return {"Đăng ký thành công"}

#--------Đăng nhập--------------#

def login_user(user: UserLogin):
    db = SessionLocal()
    db_user = db.query(Users).filter(Users.Email == user.Email).first()
    if not db_user or not verify_password(user.password, db_user.PasswordHash):
        raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng")
    
    token = create_access_token({"sub": db_user.Email})
    return {"access_token": token, "token_type": "bearer"}