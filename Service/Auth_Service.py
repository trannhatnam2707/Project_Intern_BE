from passlib.context import CryptContext  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#-----Hash mật khẩu-------#
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

#-----Kiểm tra mât khẩu-------#
def verify_password(plain_password: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_pw)

