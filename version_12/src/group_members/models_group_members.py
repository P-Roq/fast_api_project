from datetime import datetime
from typing import Union, Any, List
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    )


class GetGroupMemberShort_1(BaseModel):
    member_id: int
    group_id: int
    user_id: int
    admin: bool

class GetGroupMemberShort_2(BaseModel):
    member_id: int
    name: str
    user_id: int
    admin: bool