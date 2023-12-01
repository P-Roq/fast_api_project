from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class PostVote(BaseSettings):
    model_config = ConfigDict(extra='forbid', from_attributes=True,)
    post_id: int 
    vote: int

    @field_validator('vote')
    def validate_vote(cls, value,):
        if value not in [0, 1]:
            raise ValueError("Attribute 'vote' must be equal to 1 or -1")
        return value

