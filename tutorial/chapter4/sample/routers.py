from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from db.db import get_session
from db.model import User, Item
import auth
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
    user.password = data.password
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