from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(plain_password: str) -> str:
    """パスワードをハッシュ化する"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """plain_passwordが正しいパスワードかを検証する"""
    return pwd_context.verify(plain_password, hashed_password)