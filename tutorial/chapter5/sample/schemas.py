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