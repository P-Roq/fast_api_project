from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Union, Any


class UserBase(BaseModel):
    name: str
    email: EmailStr 
    # password: str


class GetUser(UserBase):
    user_id: int 
    name: str 
    email: str 
    created_at: datetime
    updated_at: Union[datetime, None]
    posts: int
    last_login: Union[datetime, Any]


class PostUser(UserBase):
    model_config = ConfigDict(extra='forbid')
    name:str
    email: EmailStr 
    password: str


class PatchUser(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = None
    email: EmailStr = None 
    # password: str = None
