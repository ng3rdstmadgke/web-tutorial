from session import get_session
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from model import User, Role, RoleType
import auth

def create_user(session: Session, username: str, password: str, role_type: RoleType) -> User:
    # userの重複確認
    user = session.query(User).filter(User.username == username).first()
    if user:
        raise Exception(f"{username} is already exists.")

    # roleの存在確認
    role = session.query(Role).filter(Role.name == role_type.value).first()
    if role is None:
        raise Exception(f"{role_type.value} is not exists.")

    user = User(
        username=username,
        hashed_password=auth.hash(password),
        age=20,
        roles=[role],
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user