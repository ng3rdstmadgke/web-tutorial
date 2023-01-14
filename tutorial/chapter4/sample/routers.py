from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from db.db import get_db
from db.model import User, Item
from schemas import (
    UserSchema,
)

router = APIRouter()

@router.get("/users/", response_model=List[UserSchema])
def read_users(
    skip: int = 0,  # GETパラメータ
    limit: int = 100,  # GETパラメータ
    db: Session = Depends(get_db),
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users