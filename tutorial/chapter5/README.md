# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter5/src` をルートディレクトリとして解説します。


# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter5 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter5"

# マイグレーション
alembic upgrade head
```


# ■ ログインが必要なアイテムのCRUDを実装してみましょう

## アイテムの新規作成

ログインしているユーザーでアイテムを登録するAPIを実装します。

まずは、ログインしているユーザーを取得する関数を `auth.py` に実装しましょう。  

ログイン中のユーザーは Authorizationヘッダの JWT をデコードして取得します。  
デコードの際に秘密鍵で電子署名をチェックして、JWTに改ざんがないかをチェックします。

```python
# -- auth.py --

# ... 略 ...

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from db.db import get_session
from db.model import User
from env import Environment

# ... 略 ...

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
        # JWTのデコードと電子署名のチェックを行う
        payload = jwt.decode(token, env.token_secret_key, algorithms=[env.token_algorithm])

        # デコードされたJWTのペイロードからusernameを取得
        username: str = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

次に、APIのリクエスト・レスポンスの項目と型を `schemas.py` に定義します。

```python
# -- schemas.py --

# ... 略 ...

class ItemResponseSchema(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

class ItemPostSchema(BaseModel):
    title: str
    content: str
```

アイテムの作成APIを実装します

```python
# -- routers.py --

# ... 略 ...

from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,
    ItemResponseSchema,
    ItemPostSchema,
)

# ... 略 ...

@router.post("/items/", response_model=ItemResponseSchema)
async def create(
    # request form and files: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
    data: ItemPostSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user)
):
    item = Item(title=data.title, content=data.content)
    current_user.items.append(item)
    session.add(current_user)
    session.commit()
    session.refresh(item)
    return item
```


## アイテムの一覧

アイテムの一覧表示APIを実装します

```python
# -- routers.py --

# ... 略 ...

# アイテムの一覧
@router.get("/items/", response_model=List[ItemResponseSchema])
def get_list(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user)
):
    items = session.query(Item).filter(Item.user_id == current_user.id).offset(skip).limit(limit).all()
    return items

```


## アイテムの更新


更新APIのリクエストパラメータを `schemas.py` に定義します。

```python
# -- schemas.py --

# ... 略 ...

class ItemPutSchema(BaseModel):
    title: str
    content: str
```

アイテムの更新APIを実装します

```python
# -- routers.py --

# ... 略 ...

from sqlalchemy import and_
from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,
    ItemResponseSchema,
    ItemPostSchema,
    ItemPutSchema,
)

# ... 略 ...

# アイテムの更新
@router.put("/items/{item_id}", response_model=ItemResponseSchema)
async def update(
    item_id: int,
    data: ItemPostSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user)
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
```


## アイテムの削除

アイテムの削除APIを実装します

```python
# -- routers.py

# ... 略 ...

# アイテムの削除
@router.delete("/items/{item_id}")
def delete(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user)
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
```

## ブラウザで確認してみましょう

```bash
# アプリを起動
./bin/run.sh chapter5 --mode app
```

http://127.0.0.1:8018/docs にブラウザでアクセスしてみましょう。