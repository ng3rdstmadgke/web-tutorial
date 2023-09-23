import sys
import pprint
pprint.pprint(sys.path)
sys.path.append("/opt/app/api")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from session import get_session
from model import Base, RoleType, Role
from main import app
from env import Environment
from tests.lib import create_user, fetch_token

@pytest.fixture
def client() -> TestClient:
    # セッションファクトリーの作成
    env = Environment()
    DB_URL = f"mysql+pymysql://{env.db_user}:{env.db_password}@{env.db_host}:{env.db_port}/test?charset=utf8mb4"
    engine = create_engine(DB_URL, echo=True)
    TestSessionFactory = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    # テスト用のテーブルの初期化（関数ごとにリセット）
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # DIを使ってFastAPIのDBの向き先をテスト用DBに変更
    def get_test_session():
        session = TestSessionFactory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = get_test_session

    # テスト用のロールとユーザーを作成
    with TestSessionFactory() as session:
        session.add(Role(id=1, name=RoleType.SYSTEM_ADMIN))
        session.add(Role(id=2, name=RoleType.LOCATION_ADMIN))
        session.add(Role(id=3, name=RoleType.LOCATION_OPERATOR))
        session.commit()
        create_user(session, "sys_admin"   , "password", RoleType.SYSTEM_ADMIN)
        create_user(session, "loc_admin"   , "password", RoleType.LOCATION_ADMIN)
        create_user(session, "loc_operator", "password", RoleType.LOCATION_OPERATOR)

    # テスト用のHTTPクライアントを作成
    client = TestClient(app=app)

    # テスト実行(clientはテスト関数の引数となります。)
    yield client

    # テスト関数実行後の後処理
    client.close()


def test_user_create_sys_admin(client):
    """
    RoleType.SYSTEM_ADMINロールを持つユーザーはユーザーを作成できます
    """
    token = fetch_token(client, "sys_admin", "password")
    response = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test",
            "password": "password",
            "age": 30,
            "role_ids": [1, 2],
        }
    )
    assert response.status_code == 200

def test_user_create_loc_operator(client):
    """
    RoleType.LOCATION_OPERATORロールを持つユーザーはユーザーを作成できません
    """
    token = fetch_token(client, "loc_operator", "password")
    response = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test",
            "password": "password",
            "age": 30,
            "role_ids": [1, 2],
        }
    )
    assert response.status_code == 403

def test_user_get(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
        params={"skip": 0, "limit": 10},
    )
    assert response.status_code == 200


def test_user_update(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.put(
        "/api/v1/users/3",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password": "password",
            "age": 30,
            "role_ids": [1, 2],
        }
    )
    assert response.status_code == 200

def test_user_delete(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.delete(
        "/api/v1/users/3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

def test_item_post(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.post(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "タイトル",
            "content": "本文",
        }
    )
    assert response.status_code == 200

def test_item_getAll(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.get(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        params={"skip": 0, "limit": 10},
    )
    assert response.status_code == 200

def test_item_get(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.post(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "タイトル",
            "content": "本文",
        }
    )
    id = response.json()["id"]
    response = client.get(
        f"/api/v1/items/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

def test_item_update(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.post(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "タイトル",
            "content": "本文",
        }
    )
    id = response.json()["id"]
    response = client.put(
        f"/api/v1/items/{id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "タイトル1",
            "content": "本文2",
        }
    )
    assert response.status_code == 200

def test_item_delete(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.post(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "タイトル",
            "content": "本文",
        }
    )
    id = response.json()["id"]
    response = client.delete(
        f"/api/v1/items/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
