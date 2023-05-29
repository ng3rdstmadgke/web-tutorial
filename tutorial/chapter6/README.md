[Chapter6] APIテストを実装してみよう
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter6/src` をルートディレクトリとして解説します。

chapter6では、これまでに実装したAPIのテストを実装していきましょう。

# ■ テストの実装

## テストの前後処理を実装しましょう

APIテストを行うには、テスト用のDBにアクセスするためのセッションや、初期ユーザーなどが必要です。  
Pytestでは `fixture` を利用することで、テスト関数の前後で行われる処理を定義することができます。  


まずは、テスト用のユーザーを作成するための関数を定義しましょう。  
※ ユーザー作成APIは認証・認可が必要なので、初期ユーザーの登録は直接DBに登録する形で行います。

```python
# -- tests/lib.py --

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
```

`fixture` を実装してみましょう。 `fixture` で行う処理は下記の通りです

- 前処理
    1. DBとのセッションを作るセッションファクトリーの定義
    1. テスト用のテーブルを作成
    1. `session.get_session` をオーバーライドして、向き先をテスト用のDBに変更
    1. テスト用のユーザーとロールを作成
    1. テスト用のHTTPクライアントを作成
- 後処理
    1. HTTPクライアントのクローズ



```python
# -- tests/test_main.py --
import sys
import pprint
sys.path.append("/opt/app")  # 上の階層のファイルをimportするために PYTHON_PATH に追加

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
```


## テストを実装しましょう

作成したAPIには認証・認可が必要なので、トークンを取得する関数を実装しましょう。  


```python
# -- tests/lib.py --

# ... 略 ...

def fetch_token(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/token",
        data={"username": username, "password": password}
    )
    if response.status_code != 200:
        raise Exception(f"{response.status_code}: {response.content}")
    return response.json()["access_token"]

```

ユーザー作成APIのテストを実装してみましょう。ここでは2パターンのテストを実装してみます。  

1. `RoleType.SYSTEM_ADMIN` ロールを持つユーザーによるユーザー作成  
ユーザー作成に成功する
1. `RoleType.LOCATION_OPERATOR` ロールを持つユーザーによるユーザー作成  
権限エラーでユーザー作成に失敗する



```python
# -- tests/test_main.py --

# ... 略 ...


def test_user_create_sys_admin(client):
    """
    RoleType.SYSTEM_ADMINロールを持つユーザーはユーザーを作成できます
    """
    # トークンの取得
    token = fetch_token(client, "sys_admin", "password")

    # APIへのリクエスト
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
    # レスポンスコードのチェック
    # response.json() でレスポンスの内容を取得することもできます。
    assert response.status_code == 200  # 成功

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
    assert response.status_code == 403  # 失敗 (403 Forbidden)
```

残りのテストを実装しましょう。

```python
# -- tests/test_main.py --

# ... 略 ...

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

def test_item_get(client):
    token = fetch_token(client, "sys_admin", "password")
    response = client.get(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {token}"},
        params={"skip": 0, "limit": 10},
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
```


# ■ テストの実行

MySQLを起動し、開発用shellを起動します。
```bash
# MySQL起動
./bin/mysql.sh

# 開発用shellを起動
./bin/run.sh chapter6 --mode shell
```

※ 以下、開発用shell内での操作

```bash
# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS test"

# テストを実行
pytest tests

exit
```

# ■ スクリプトの作成

## テストスクリプト

テストのためにいちいち複数のコマンドを実行するのは手間なので、スクリプト化してしまいましょう。

```bash
# --- bin/test.sh ---
#!/bin/bash

set -e

# データベースを削除
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "DROP DATABASE IF EXISTS test"

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS test"

# テストを実行
pytest tests
```

テストスクリプトを実行してみましょう

```bash
# 開発用shellを起動
./bin/run.sh chapter6 --mode shell

# 実行権限を付与
chmod 755 ./bin/test.sh

# テストの実行
./bin/test.sh

exit
```

## DBの初期化スクリプト

毎回DBとテーブルを作成して、テスト用のユーザーを作成するのも手間なので、これらもスクリプト化してしまいましょう。

```bash
# --- bin/init-database.sh --
#!/bin/bash

# set -e : コマンドのreturn_codeが0以外だったら終了
# set -x : デバッグログを表示
set -ex

# このスクリプトの絶対パス
SCRIPT_DIR=$(cd $(dirname $0); pwd)

# プロジェクトルートの絶対パス
ROOT_DIR=$(cd $(dirname $0)/..; pwd)

cd $ROOT_DIR

# データベースを削除
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "DROP DATABASE IF EXISTS $DB_NAME"

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS $DB_NAME"

# マイグレーション
alembic upgrade head

# 初期ユーザー作成
PASSWD="admin"
python manage.py create-user sys_admin -r SYSTEM_ADMIN -p $PASSWD
python manage.py create-user loc_admin -r LOCATION_ADMIN -p $PASSWD
python manage.py create-user loc_operator -r LOCATION_OPERATOR -p $PASSWD
```

スクリプトを実行してみましょう

```bash
# 開発用shellを起動
./bin/run.sh chapter6 --mode shell

# 実行権限を付与
chmod 755./bin/init-database.sh

# DBの初期化を実行
./bin/init-database.sh

exit
```