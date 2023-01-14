# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter4/src` をルートディレクトリとして解説します。


# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter4 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter4"

# マイグレーション
alembic upgrade head
```


# ■ ユーザーのCRUDを実装してみましょう


## ユーザー作成API

username, password, ageをPOSTで受け取って、ユーザー作成を行うAPIを実装します。

まず、パスワードをハッシュ化する関数を `auth.py` に実装します。

```python
# -- auth.py --
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)
```

次に、POSTで受け取るデータとレスポンスで返却するデータの構造をクラスとして定義します。
FastAPIでは、 `pydantic` を利用して、リクエスト・レスポンスデータをオブジェクトとして扱います。

```python
# -- schemas.py --

from typing import Optional
from pydantic import BaseModel

class UserResponseSchema(BaseModel):
    """レスポンスで返却する項目と型を定義するクラス"""
    id: int
    username: str
    age: Optional[int]

    class Config:
        # orm_mode = True とすると、DBのレスポンスをシームレスにオブジェクトに変換できる
        orm_mode = True

class UserPostSchema(BaseModel):
    """ユーザー作成APIのリクエストとして渡されるパラメータと型を定義"""
    username: str
    password: str
    age: int
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
# -- routers --
from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from db.db import get_session
from db.model import User, Item
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
    db: Session = Depends(get_session),
):
    # ユーザーの存在チェック
    user = db.query(User).filter(User.username == data.username).first()
    if user:
        raise HTTPException(status_code=400, detail=f"{data.username} is already exists.")

    # ユーザーの作成
    user = User(
        username=data.username,
        hashed_password=auth.hash(data.password),  # パスワードはハッシュ化して登録
        age=data.age,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```


最後に routers.py で定義したルートをFastAPIインスタンスに登録します。

`app.include_router(router, prefix="/api/v1")` のように登録し、prefix引数を指定することでパスにプレフィックスを設定することができます。  
例えば `prefix="/api/v1"` なら今回作成したAPIのパスは `/api/v1/users` となります。  



```python
# -- main.py --

from fastapi import FastAPI
from routers import router

app = FastAPI()

app.include_router(router, prefix="/api/v1")
```

## ユーザー一覧API

ユーザーの一覧を取得するAPIを実装します。

ユーザーの一覧はGETメソッドでリクエストされるため、 `@router.get("/users/", response_model=List[UserResponseSchema])` のようにルートを定義します。  
一覧表示では、複数のユーザーがレスポンスされるため、 `response_model` は `List[UserResponseSchema]` とします。

GETパラメータとして受け取る `skip` `limit` は `read_users` 関数の引数に定義します。

```python
# -- routers.py --

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
# -- schemas.py --

# ... 略 ...

class UserPutSchema(BaseModel):
    password: str
    age: int
```

ユーザーの一覧はPUTメソッドでリクエストされるため、 `@router.put("/users/{user_id}", response_model=UserResponseSchema)` のようにルートを定義します。  

```python
# -- routers.py

# ... 略 ...

from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,
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

    # リクエストで受け取った password と age を設定して保存
    user.password = data.password
    user.age = data.age
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```



## ユーザー削除API

指定したユーザーを削除するAPIを実装します。

ユーザーの一覧はDELETEメソッドでリクエストされるため、 `@router.delete("/users/{user_id}")` のようにルートを定義します。  

```python
# -- routers.py

# ... 略 ...

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
```

## ブラウザで確認してみましょう

```bash
# アプリを起動
./bin/run.sh chapter4 --mode app
```

http://127.0.0.1:8018/docs にブラウザでアクセスしてみましょう。


# ■ ログイン用のAPIを作成する

参考: [JWT token with scopes | FastAPI](https://fastapi.tiangolo.com/ja/advanced/security/oauth2-scopes/?h=token#jwt-token-with-scopes)

usernameとpasswordを受け取ってtokenを生成するAPIを実装していきます。

まず、環境変数に token_expire_minute (トークンの有効期限) , token_secret_key (トークンを暗号化する秘密鍵) , token_algorithm (トークンの暗号化方式) を追加していきます。

```python
# -- env.py --

from pydantic import BaseSettings

class Environment(BaseSettings):
    # ... 略 ...
    token_expire_minutes: int = 480
    token_secret_key: str = "1234567890"
    token_algorithm: str = "HS256"
```

次に、 `auth.py` に入力されたパスワードとDBに登録しあるパスワードの検証をおなう関数を追加します。

```python
# -- auth.py --

# ... 略 ...

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """plain_passwordが正しいパスワードかを検証する"""
    return pwd_context.verify(plain_password, hashed_password)
```

最後に、トークンを取得するAPIを追加します。

```python
# -- routers.py --

# ... 略 ...

from env import Environment
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, HTTPException, status
from datetime import timedelta, datetime
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
        "exp": datetime.utcnow() + timedelta(minutes=env.token_expire_minutes)
    }

    # トークンの生成
    access_token = jwt.encode(payload, env.token_secret_key, algorithm=env.token_algorithm)
    return {"access_token": access_token, "token_type": "bearer"}
```

## ブラウザで確認してみましょう

```bash
# アプリを起動
./bin/run.sh chapter4 --mode app
```

http://127.0.0.1:8018/docs にブラウザでアクセスしてみましょう。