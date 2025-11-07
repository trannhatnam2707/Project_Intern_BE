from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from Models.Users_Model import Users
from Service.JWT_Service import verify_access_token
from Database.Connection import SessionLocal

#------Dependency để lấy token cho user-------#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

#------Dependency để lấy db-------#
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
#------Dependency để lấy user hiện tại từ token-------#
def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = verify_access_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
        user = db.query(Users).filter(Users.Email == email).first()
        if not user:                                                
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Người dùng không tồn tại")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ hoặc đã hết hạn")

def require_admin(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = verify_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        
        user = db.query(Users).filter(Users.Email == email).first()
        if not user or user.Role != "admin":
            raise HTTPException(status_code=403, detail="Không có quyền admin")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token hết hạn hoặc không hợp lệ")