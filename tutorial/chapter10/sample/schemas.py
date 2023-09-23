from typing import Optional, List
from pydantic import ConfigDict, BaseModel

class RoleSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class UserResponseSchema(BaseModel):
    """レスポンスで返却する項目と型を定義するクラス"""
    id: int
    username: str
    age: Optional[int]
    roles: List[RoleSchema]

    # from_attributes = True : DBのレコードをシームレスにオブジェクトに変換できる
    model_config = ConfigDict(from_attributes=True)

class UserPostSchema(BaseModel):
    """ユーザー作成APIのリクエストとして渡されるパラメータと型を定義"""
    username: str
    password: str
    age: int
    role_ids: List[int]

class UserPutSchema(BaseModel):
    password: str
    age: int
    role_ids: List[int]

class ItemResponseSchema(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)

class ItemPostSchema(BaseModel):
    title: str
    content: str

class ItemPutSchema(BaseModel):
    title: str
    content: str