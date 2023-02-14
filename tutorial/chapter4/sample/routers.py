from typing import List
from datetime import timedelta, datetime

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, HTTPException, status
from jose import jwt, JWTError

from db.db import get_session
from db.model import User, Item
import auth
from env import Environment
from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,
)

router = APIRouter()

# ユーザー作成
@router.post("/users/", response_model=UserResponseSchema)
def create_user(
   data: UserPostSchema, 
    session: Session = Depends(get_session),
):
    user = session.query(User).filter(User.username == data.username).first()
    if user:
        raise HTTPException(status_code=400, detail=f"{data.username} is already exists.")

    user = User(
        username=data.username,
        hashed_password=auth.hash(data.password),
        age=data.age,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# ユーザー一覧
@router.get("/users/", response_model=List[UserResponseSchema])
def read_users(
    skip: int = 0,  # GETパラメータ
    limit: int = 100,  # GETパラメータ
    session: Session = Depends(get_session),
):
    users = session.query(User).offset(skip).limit(limit).all()
    return users

# ユーザー更新
@router.put("/users/{user_id}", response_model=UserResponseSchema)
def update_user(
    user_id: int,
    data: UserPutSchema,
    session: Session = Depends(get_session),
):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User is not found. (id={user_id})")
    user.hashed_password = auth.hash(data.password)
    user.age = data.age
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# ユーザー削除
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User is not found. (id={user_id})")
    session.delete(user)
    session.commit()
    return {"user_id": user_id}

# トークン取得API
@router.post("/token")
def login_for_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    env = Environment()
    # OAuth2PasswordRequestForm は username, password, scope, grant_type といったメンバを持つ
    # https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
    user = session.query(User).filter(User.username == form_data.username).first()
    if (user is None) or (not auth.verify_password(form_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload={
        # JWT "sub" Claim : https://openid-foundation-japan.github.io/draft-ietf-oauth-json-web-token-11.ja.html#subDef
        "sub": user.username,
        "scopes": [],
        "exp": datetime.utcnow() + timedelta(minutes=env.token_expire_minutes)
    }

    # トークンの生成
    access_token = jwt.encode(payload, env.token_secret_key, algorithm=env.token_algorithm)
    return {"access_token": access_token, "token_type": "bearer"}