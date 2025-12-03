from datetime import datetime, timedelta
import os
from fastapi import HTTPException, status
from dotenv import load_dotenv
from jose import jwt , JWTError



load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


#-----Tạo access token-------#
def create_access_token(data: dict, expires_delta: timedelta | None = None ) -> str:
    to_endcode = data.copy()
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    
    x
    if "type" not in to_endcode:
        to_endcode.update({"type": "access"})
        
    to_endcode.update({"exp": expires})
    
    encoded_jwt = jwt.encode(to_endcode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#------Tạo refresh token-------#
def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_endcode = data.copy()
    expires = datetime.utcnow() + (expires_delta or timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS)))
    to_endcode.update({"exp": expires, "type": "refresh"})
    encoded_jwt = jwt.encode(to_endcode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#------Giải mã JWT-------#
def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired access token")
    
#------Giải mã Refresh JWT-------#
def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired refresh token")
    
def verify_reset_token(token:  str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Kiểm tra đúng là token loại "reset" không
        if payload.get("type") != "reset":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid token type")
        return payload
    except JWTError:    
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired reset token")