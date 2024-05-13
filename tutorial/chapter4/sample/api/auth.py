import bcrypt

def hash(plain_password: str) -> str:
    """パスワードをハッシュ化する"""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """plain_passwordが正しいパスワードかを検証する"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))