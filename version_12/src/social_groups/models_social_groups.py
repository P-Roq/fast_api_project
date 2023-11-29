from datetime import datetime
from typing import Union, Any, List
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    )

class AdminInfo(BaseModel):
    user_id: int
    name: str
    email: EmailStr


class GetSocialGroup(BaseModel):
    group_id: int
    admin_id: float
    admin_name: str
    title: str 
    details: str
    created_at: datetime
    updated_at: Union[datetime, None] 
    members: int


class GetAllSocialGroups(BaseModel):
    group_id: int
    title: str 
    details: str
    created_at: datetime
    updated_at: Union[datetime, None]
    admin_info:  AdminInfo
    members: int

class PostCreateSocialGroup(BaseModel):
    model_config = ConfigDict(extra='forbid',) 
    title: str 
    details: str 