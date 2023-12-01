from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    username: EmailStr # attribute name changed to accommodate `OAuth2PasswordRequestForm` requirements.
    password: str

class GetToken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None