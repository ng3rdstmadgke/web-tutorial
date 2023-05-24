[Chapter5] 認証・認可が必要なAPIを実装してみよう
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter5/src` をルートディレクトリとして解説します。

chapter5では、認証・認可が必要なAPIを実装していきましょう。

# ■ mysqlを起動しましょう

※ 起動していない場合のみ

```bash
./bin/mysql.sh
```

# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter5 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter5"

# マイグレーション
alembic upgrade head
```


# ■ ログインが必要なAPIを実装してみましょう

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
from session import get_session
from model import User
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
    ItemResponseSchema,  # 追加
    ItemPostSchema,  # 追加
)

# ... 略 ...

@router.post("/items/", response_model=ItemResponseSchema)
def create(
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

from sqlalchemy import and_  # 追加
from schemas import (
    UserResponseSchema,
    UserPostSchema,
    UserPutSchema,
    ItemResponseSchema,
    ItemPostSchema,
    ItemPutSchema,  # 追加
)

# ... 略 ...

# アイテムの更新
@router.put("/items/{item_id}", response_model=ItemResponseSchema)
def update(
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


# ■ ロールでアクセスが制限されるAPIを実装してみましょう

今回は各ロールに下記の権限を許可してみましょう

- SYSTEM_ADMIN
  - アイテム作成
  - アイテム閲覧
  - アイテム更新
  - アイテム削除
- LOCATION_ADMIN
  - アイテム作成
  - アイテム削除
- LOCATION_OPERATOR
  - アイテム作成

権限の定義と、権限の有無を確認するユーティリティを実装します。

```python
# -- permission_service.py --

import enum
from typing import Dict, Set, List, Callable
from model import User, RoleType
from functools import wraps

# 権限の定義
class PermissionType(enum.Enum):
    ITEM_CREATE = "ITEM_CREATE"
    ITEM_READ   = "ITEM_READ"
    ITEM_UPDATE = "ITEM_UPDATE"
    ITEM_DELETE = "ITEM_DELETE"

# 権限を扱うユーティリティクラス
class PermissionService:
    # どのロールが何の権限を持っているのかをクラス変数で定義
    __role_definition: Dict[RoleType, Set[PermissionType]] = {
        RoleType.SYSTEM_ADMIN: set([  # SYSTEM_ADMIN が保有する権限
            PermissionType.ITEM_CREATE,
            PermissionType.ITEM_READ,
            PermissionType.ITEM_UPDATE,
            PermissionType.ITEM_DELETE,
        ]),
        RoleType.LOCATION_ADMIN: set([  # LOCATION_ADMIN が保有する権限
            PermissionType.ITEM_CREATE,
            PermissionType.ITEM_DELETE,
        ]),
        RoleType.LOCATION_OPERATOR: set([  # LOCATION_OPERATOR が保有する権限
            PermissionType.ITEM_CREATE,
        ])
    }

    @classmethod
    def has_permission(cls, user: User, permissions: List[PermissionType]) -> bool:
        """引数で受け取った権限を有しているかを確認するメソッド"""
        required_permissions = set(permissions)
        user_permissions = cls.get_permissions(user)
        return len(required_permissions) == len(required_permissions & user_permissions)

    @classmethod
    def get_permissions(cls, user: User) -> Set[PermissionType]:
        """ユーザーが保持している権限を取得するメソッド"""
        ret = set()
        for role in user.roles:
            ret = ret | cls.__role_definition.get(role.name, set())
        return ret

```

次に、 `auth.py` の `get_current_user` を編集しましょう。  
引数で権限の配列を受け取り、`_get_current_user` というクロージャーを返却するメソッドに書き換えます。

```python
# -- auth.py --

# ... 略 ...
from typing import List, Callable
from permission_service import PermissionType, PermissionService

# ... 略 ...


def get_current_user(permissions: List[PermissionType] = []) -> Callable:
    def _get_current_user(
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
            payload = jwt.decode(token, env.token_secret_key, algorithms=[env.token_algorithm])
            username: str = payload["sub"]
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = session.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
    
        # 要求された権限を持っているかを確認
        if not PermissionService.has_permission(user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    return _get_current_user
```


最後にAPIの `auth.get_current_user` を `auth.get_current_user([権限名])` に書き換えていきます。

```python
# -- routers.py --

# ... 略 ...
from permission_service import PermissionType

# アイテムの新規作成
@router.post("/items/", response_model=ItemResponseSchema)
def create(
    data: ItemPostSchema,
    session: Session = Depends(get_session),
    # get_current_userの引数にこのAPIを実行するために必要な権限の配列を指定
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_CREATE]))  # 変更
):
    # ... 略 ...

# アイテムの一覧
@router.get("/items/", response_model=List[ItemResponseSchema])
def get_list(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_READ]))  # 変更
):
    # ... 略 ...


# アイテムの更新
@router.put("/items/{item_id}", response_model=ItemResponseSchema)
def update(
    item_id: int,
    data: ItemPostSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_UPDATE]))  # 変更
):
    # ... 略 ...

# アイテムの削除
@router.delete("/items/{item_id}")
def delete(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user([PermissionType.ITEM_DELETE]))  # 変更
):
    # ... 略 ...
```

## ブラウザで確認してみましょう


```bash
# アプリを起動
./bin/run.sh chapter5 --mode app
```