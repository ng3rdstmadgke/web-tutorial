from typing import List
from datetime import timedelta, datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, HTTPException, status
from jose import jwt, JWTError

from session import get_session
from model import User, Item, Role
import auth
from env import Environment
from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,
    ItemResponseSchema,
    ItemPostSchema,
    ItemPutSchema,
)

from permission_service import PermissionType


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

    # idからロールを取得
    roles = []
    for role_id in data.role_ids:
        role = session.query(Role).filter(Role.id == role_id).first()
        if role is None:
            raise HTTPException(status_code=404, detail=f"Role is not found. (id={role_id})")
        roles.append(role)

    user = User(
        username=data.username,
        hashed_password=auth.hash(data.password),
        age=data.age,
        roles=roles,
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

# ユーザー取得
@router.get("/users/{user_id}", response_model=UserResponseSchema)
def read_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User is not found. (id={user_id})")
    return user

# ユーザー更新
@router.put("/users/{user_id}", response_model=UserResponseSchema)
def update_user(
    user_id: int,
    data: UserPutSchema,
    session: Session = Depends(get_session),
):
    # ユーザーの存在チェック。更新対象のユーザーが存在しなければ404エラー
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User is not found. (id={user_id})")

    # idからロールを取得
    roles = []
    for role_id in data.role_ids:
        role = session.query(Role).filter(Role.id == role_id).first()
        if role is None:
            raise HTTPException(status_code=404, detail=f"Role is not found. (id={role_id})")
        roles.append(role)

    # リクエストで受け取った password と age を設定して保存
    user.hashed_password = auth.hash(data.password)
    user.age = data.age
    user.roles = roles
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
    # ユーザーの存在チェック。更新対象のユーザーが存在しなければ404エラー
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


# アイテムの新規作成
@router.post("/items/", response_model=ItemResponseSchema)
async def create(
    # request form and files: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
    data: ItemPostSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_CREATE]))
):
    item = Item(title=data.title, content=data.content)
    current_user.items.append(item)
    session.add(current_user)
    session.commit()
    session.refresh(item)
    return item


# アイテムの一覧
@router.get("/items/", response_model=List[ItemResponseSchema])
def get_list(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_READ]))
):
    items = session.query(Item).filter(Item.user_id == current_user.id).offset(skip).limit(limit).all()
    return items


# アイテムの更新
@router.put("/items/{item_id}", response_model=ItemResponseSchema)
async def update(
    item_id: int,
    data: ItemPostSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_UPDATE]))
):
    item = session.query(Item).filter(and_(Item.id == item_id, Item.user_id == current_user.id)).first()
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")

    try:
        item.title = data.title
        item.content = data.content
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# アイテムの削除
@router.delete("/items/{item_id}")
def delete(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_DELETE]))
):
    item = session.query(Item).filter(and_(Item.id == item_id, Item.user_id == current_user.id)).first()
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    try:
        session.delete(item)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"item_id": item_id}