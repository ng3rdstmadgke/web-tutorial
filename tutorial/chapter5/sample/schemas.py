from typing import Optional
from pydantic import BaseModel

class UserResponseSchema(BaseModel):
    id: int
    username: str
    age: Optional[int]

    class Config:
        orm_mode = True

class UserPostSchema(BaseModel):
    username: str
    password: str
    age: int

class UserPutSchema(BaseModel):
    password: str
    age: int

class ItemResponseSchema(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

class ItemPostSchema(BaseModel):
    title: str
    content: str

class ItemPutSchema(BaseModel):
    title: str
    content: str