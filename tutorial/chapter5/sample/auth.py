from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from db.db import get_session
from db.model import User
from env import Environment

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(plain_password: str) -> str:
    """パスワードをハッシュ化する"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """plain_passwordが正しいパスワードかを検証する"""
    return pwd_context.verify(plain_password, hashed_password)

# OAuth2PasswordBearerのインスタンスをDependsで解決すると、
# RequestのAuthorizationヘッダが `Bearer {token}` 形式であることを確認し、tokenをstrで返す
# 引数の tokenUrl には token を取得するURLを指定する。(swagger UIのAuthorizeの宛先になる)
# もしAuthorizationヘッダがなかったり、 値の形式が異なっていた場合は、401ステータスエラー(UNAUTHORIZED)を返す。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
    ) -> User:
    """JWTの署名検証を行い、subに格納されているusernameからUserオブジェクトを取得する
    引数のtokenには "/api/v1/token" でリターンした access_token が格納されている
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    env = Environment()
    try:
        payload = jwt.decode(token, env.token_secret_key, algorithms=[env.token_algorithm])
        username: str = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user