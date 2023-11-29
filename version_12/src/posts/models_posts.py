from datetime import datetime
from typing import Union, Any, List
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,    
    )
from src.users.models_users import UserBase


class PostPost(BaseModel):
    model_config = ConfigDict(extra='forbid',) 
    view_count: int 
    title: str 


class PutPost(BaseModel):
    model_config = ConfigDict(extra='forbid',) 
    view_count: int = None
    title: str = None
    # secret_number: int 


class GetPost(BaseModel):
    post_id: int
    # score: float
    view_count: int 
    title: str
    created_at: datetime
    updated_at: Union[datetime, None] 
    # user_id: Union[int, None]
    user_info: UserBase
    upvotes: int


class GetAllPosts(BaseModel):
    post_id: int
    # score: float
    view_count: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: Union[datetime, None]
    author: str
    email: EmailStr
    upvotes: int

class PatchPost(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True,)
    view_count: int = None
    title: str = None
    # secret_number: int = None
  