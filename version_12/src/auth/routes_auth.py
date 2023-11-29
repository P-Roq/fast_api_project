from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends,  status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from src.utils import validate_pw
from src.auth.models_auth import GetToken
from src.oauth2 import create_access_token
from src.database.db_setup import Session, get_db
from src.database.db_models import DBSessionUsers
from src.database.http_exceptions import (
    check_object_availability,
    check_password,
    check_add_resource,
)

router = APIRouter()

# Important note: `OAuth2PasswordRequestForm` only accepts two default fields: `username` and `password`, therefore, we changed our pydantic input validation
# class attribute `email` to `username` but we still use it to store the email as part of the login credentials.

@router.post("/", response_model=GetToken)
def send_login_credentials(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    ):

    db_session = DBSessionUsers(db,)
    email = user_credentials.username # login email
    password = user_credentials.password # login password

    resource = db_session.fetch_resource({'email': email}, False)
    
    check_object_availability(resource, f'Invalid credentials', 403)

    hashed_pw = resource.password
    user_id = resource.user_id

    check_password(validate_pw(password, hashed_pw))

    access_token = create_access_token(data = {"user_id": user_id}) # user ID embedded into the token.

    check_add_resource(
        lambda: db_session.update_resource(id_column='user_id', id=user_id, dump={'last_login': datetime.utcnow()}),
        status_code=500,
        )

    return {"access_token": access_token, "token_type": "bearer"}


