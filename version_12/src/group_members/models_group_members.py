from datetime import datetime
from typing import Union, Any, List
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    )


class GetGroupMemberShort(BaseModel):
    member_id: int
    group_id: int
    user_id: int
    admin: bool
    total_posts: Union[int, None]


class GetGroupMember(GetGroupMemberShort):
    created_at: datetime
    updated_at: Union[datetime, None]
    name: str
    email: EmailStr

class PostGroupMember(BaseModel):
    model_config = ConfigDict(extra='forbid',)
    group_id: int