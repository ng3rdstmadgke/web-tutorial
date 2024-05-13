[Chapter4] FastAPIでCRUDを実装してみよう
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter4/src` をルートディレクトリとして解説します。  
chapter4では、userの登録・閲覧・編集・削除を行うAPIを作成します。  

# ■ mysqlを起動しましょう

※ 起動していない場合のみ

```bash
./bin/mysql.sh
```


# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter4 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter4"

# マイグレーション
alembic upgrade head
```

# ■ アプリの起動

アプリを起動して、ブラウザで確認しながら実装していきましょう

```bash
# アプリを起動
./bin/run.sh chapter4 --mode app
```

http://127.0.0.1:8018/docs にブラウザでアクセス


# ■ pydantic を使ってみましょう

FastAPIで欠かせないライブラリが `pydantic` です。ここでは `pydantic` のメリットや実際にどのように利用するのかを学習しましょう。

従来のPythonプログラムでは、データを配列や辞書形式で扱うことが多かったのではないでしょうか。  
Pythonは動的型付け言語なので、型に関する制約がゆるく、型を意識せずともなんとなく書けてしまうといった特徴があります。  
しかし、型が緩く、データを配列や辞書で扱うといった特徴は、継続的な運用と開発が行われるシステムにおいては非常に大きなデメリットととなります。

次の関数を見てください。この関数が引数としてどのようなデータを受け取って、戻り値としてどのようなデータを返却するかわかるでしょうか。  

```python
def create_user(session, data):
    ret = {
        "roles" = []
    }
    user = session.query(User).filter(User.username == data["user"]["username"]).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registerd")
    roles = []
    for e in data["roles"]:
        role = session.query(Role).filter(Role.name == e["name"]).first()
        roles.append(role if (role) else Role(name=e["name"]))
    user = User(
        username=data["user"]["username"],
        hashed_password=auth.get_password_hash(data.["user"]["password"]),
        age=data["user"]["age"],
        roles=roles,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    ret["id"] = user.id
    ret["username"] = user.username
    ret["age"] = user.age
    for item in user.roles:
        ret["roles"]["name"] = item.name
    return ret
```

おそらくぱっと見でわかる人はいないでしょう。例はまだましな部類ですが、運用を続けていくと機能はより複雑になり、数も増えていきます。  
そうなると、この関数とそれを利用するコードの修正コストは非常に大きくなり、バグも発生しやすくなります。 (システムの硬直化と言ったりします)

それを解決するのが `pydantic` というライブラリです。
このライブラリ、機能としてはクラスと辞書とjsonをシームレスに変換するだけですので、少し使い方を確認してみましょう。

```python
from typing import List, Optional
from pydantic import ConfigDict, BaseModel


class User(BaseModel):
    id: int
    username: str
    age: int

data = {
    "id": 1,
    "username": "yamada",
    "age": 35,
}

# dataをUserオブジェクトに変換
user = User.parse_obj(data)
print(user)  # id=1 username='yamada' age=35

# Userオブジェクトをdictに変換
user_dict = user.dict()
print(user_dict)  # {'id': 1, 'username': 'yamada', 'age': 35}

# Userオブジェクトをjsonに変換
user_json = user.json()
print(user_json)  # {"id": 1, "username": "yamada", "age": 35}
```

機能としてはシンプルですが、これを先ほどの関数の引数と戻り値の型に適用すると、受け取る値と返す値が明確になり、修正しやすくバグが発生しにくいコードとなります。  
FastAPIではこの `pydantic` を使って、APIが受け取る値と返す値の構造を明確に定義します。


```python
from typing import List, Optional
from pydantic import ConfigDict, BaseModel

class User(BaseModel):
    username: str
    password: str
    age: int

class Role(BaseModel):
    name: str

class RequestData(BaseModel):
    user: User
    roles: List[Role]

class ResponseData(BaseModel):
    id: int
    username: str
    age: int
    roles: List[Role]

def create_user(session: Session, data: RequestData) -> ResponseData :
    user = session.query(User).filter(User.username == data.user.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registerd")
    roles = []
    for e in data.roles:
        role = session.query(Role).filter(Role.name == e.name).first()
        roles.append(role if (role) else Role(name=e.name))
    user = User(
        username=data.user.username,
        hashed_password=auth.get_password_hash(data.user.password),
        age=data.user.age,
        roles=roles,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return ResponseData.from_orm(user)
```


# ■ ユーザーのCRUDを実装してみましょう


## ユーザー作成API

username, password, ageをPOSTで受け取って、ユーザー作成を行うAPIを実装してみましょう。

パスワードはプレーンテキストでDBに保存するわけにはいかないので、不可逆のハッシュ値に変換します。  
`auth.py` にパスワードをハッシュ化する関数を実装しましょう。


```python
# -- api/auth.py --
import bcrypt

def hash(plain_password: str) -> str:
    """パスワードをハッシュ化する"""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```

次に、POSTで受け取るデータとレスポンスで返却するデータの構造をクラスとして定義しましょう。
FastAPIでは、 `pydantic` を利用して、リクエスト・レスポンスデータをオブジェクトとして扱います。

```python
# -- api/schemas.py --

from typing import Optional, List
from pydantic import ConfigDict, BaseModel

class RoleSchema(BaseModel):
    id: int
    name: str

    # from_attributes = True : DBのレコードをシームレスにオブジェクトに変換できる
    model_config = ConfigDict(from_attributes=True)

class UserResponseSchema(BaseModel):
    """レスポンスで返却する項目と型を定義するクラス"""
    id: int
    username: str
    age: Optional[int]
    roles: List[RoleSchema]

    model_config = ConfigDict(from_attributes=True)

class UserPostSchema(BaseModel):
    """ユーザー作成APIのリクエストとして渡されるパラメータと型を定義"""
    username: str
    password: str
    age: int
    role_ids: List[int]
```

APIの本体を実装します。

ユーザーの作成はPOSTメソッドでリクエストされるため、 `@router.post("/users/", response_model=UserResponseSchema)` のようにルートを定義します。  
 `response_model` に先ほど定義した `UserResponseSchema` を指定することで、レスポンスする項目と型をソースコード上に明示することができます。

`create_user` 関数の引数の `data: UserPostSchema` はリクエストとして渡されるパラメータを受け取っています。

`create_user` 関数の引数の `db: Session = Depends(get_session)` はデータベースとのセッションを受け取っています。  
`Depends(get_session)` とすることで `get_session` 関数を実行して戻り値であるsessionを受け取っています。  
このように依存オブジェクトを引数から受けとることを Dependency Injection (DI) と呼び、関数が他のオブジェクトに依存しなくなることで、テストしやすくなります。  
FastAPIはフレームワーク自体にDIの仕組みがあります。 ( [Dependencies | FastAPI](https://fastapi.tiangolo.com/ja/tutorial/dependencies/) )


```python
# -- api/routers.py --

from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from session import get_session
from model import User, Item, Role
import auth
from schemas import (
    UserResponseSchema,
    UserPostSchema,
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
```


最後に routers.py で定義したルートをFastAPIインスタンスに登録します。

`app.include_router(router, prefix="/api/v1")` のように登録し、prefix引数を指定することでパスにプレフィックスを設定することができます。  
例えば `prefix="/api/v1"` なら今回作成したAPIのパスは `/api/v1/users` となります。  



```python
# -- api/main.py --

from fastapi import FastAPI
from routers import router

app = FastAPI()

app.include_router(router, prefix="/api/v1")
```

## ユーザー取得API

ユーザーIDを指定してユーザーを取得するAPIを実装します。

ユーザーの取得はGETメソッドでリクエストされるため、 `@router.get("/users/{user_id}", response_model=UserResponseSchema)` のようにルートを定義します。  
取得するユーザーはユーザーIDで指定するのでパスパラメータに `user_id` を設定します。

```python
# -- api/routers.py --

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
```

## ユーザー一覧API

ユーザーの一覧を取得するAPIを実装します。

ユーザーの一覧はGETメソッドでリクエストされるため、 `@router.get("/users/", response_model=List[UserResponseSchema])` のようにルートを定義します。  
一覧表示では、複数のユーザーがレスポンスされるため、 `response_model` は `List[UserResponseSchema]` とします。

GETパラメータとして受け取る `skip` `limit` は `read_users` 関数の引数に定義します。

```python
# -- api/routers.py --

# ... 略 ...

# ユーザー一覧
@router.get("/users/", response_model=List[UserResponseSchema])
def read_users(
    skip: int = 0,  # GETパラメータ
    limit: int = 100,  # GETパラメータ
    session: Session = Depends(get_session),
):
    users = session.query(User).offset(skip).limit(limit).all()
    return users
```

## ユーザー更新API

指定したユーザーの password と age を更新するAPIを実装します。

まずは、更新APIが受け取るパラメータの定義を `schemas.py` に実装します。

```python
# -- api/schemas.py --

# ... 略 ...

class UserPutSchema(BaseModel):
    password: str
    age: int
    role_ids: List[int]
```

ユーザーの一覧はPUTメソッドでリクエストされるため、 `@router.put("/users/{user_id}", response_model=UserResponseSchema)` のようにルートを定義します。  

```python
# -- api/routers.py --

# ... 略 ...

from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,  # 追加
)

# ... 略 ...

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
```


## ユーザー削除API

指定したユーザーを削除するAPIを実装します。

ユーザーの一覧はDELETEメソッドでリクエストされるため、 `@router.delete("/users/{user_id}")` のようにルートを定義します。  

```python
# -- api/routers.py --

# ... 略 ...

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
```

## ブラウザで確認してみましょう

```bash
# アプリを起動
./bin/run.sh chapter4 --mode app
```

http://127.0.0.1:8018/docs にブラウザでアクセスしてみましょう。


# ■ ログイン用のAPIを作成する

- [基本から理解するJWTとJWT認証の仕組み](https://developer.mamezou-tech.com/blogs/2022/12/08/jwt-auth/)
- [JWT token with scopes | FastAPI](https://fastapi.tiangolo.com/ja/advanced/security/oauth2-scopes/?h=token#jwt-token-with-scopes)

usernameとpasswordを受け取ってtokenを生成するAPIを実装していきます。

まず、環境変数に token_expire_minute (トークンの有効期限) , token_secret_key (トークンを暗号化する秘密鍵) , token_algorithm (トークンの暗号化方式) を追加していきます。

```python
# -- api/env.py --

from pydantic_settings import BaseSettings

class Environment(BaseSettings):
    # ... 略 ...
    token_expire_minutes: int = 480
    token_secret_key: str = "1234567890"
    token_algorithm: str = "HS256"
```

次に、 `auth.py` に入力されたパスワードとDBに登録しあるパスワードの検証をおなう関数を追加します。

```python
# -- api/auth.py --

# ... 略 ...

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """plain_passwordが正しいパスワードかを検証する"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
```

最後に、トークンを取得するAPIを追加します。

```python
# -- api/routers.py --

# ... 略 ...

from env import Environment
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, HTTPException, status
from datetime import timedelta, datetime, UTC
from jose import jwt, JWTError

# ... 略 ...


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
        "exp": datetime.now(UTC) + timedelta(minutes=env.token_expire_minutes)
    }

    # トークンの生成
    access_token = jwt.encode(payload, env.token_secret_key, algorithm=env.token_algorithm)
    return {"access_token": access_token, "token_type": "bearer"}
```
