import os
from typing import Callable
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.env_models import settings
from src.auth.models_auth import TokenData 
from src.route_config import LOGIN_ROUTE
from src.database.db_setup import get_db
from src.database.db_models import DBSession, Users

oauth_scheme = OAuth2PasswordBearer(tokenUrl=LOGIN_ROUTE)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.expiration_time)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, settings.key_token, algorithm=settings.algorithm,)

    return encoded_jwt


def verify_access_token(
    token: str,
    credentials_exception: HTTPException,
    credentials_exception_expiration_check: HTTPException
    ) -> TokenData:

    # Time validation.
    try:
        decoded_token = jwt.decode(token, settings.key_token, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError:
        raise credentials_exception_expiration_check
    
    # Credential (user ID in this case) validation.
    try:
        decoded_token = jwt.decode(token, settings.key_token, algorithms=[settings.algorithm])

        id: str = decoded_token.get('user_id')

        if id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=id)
    
    except JWTError:
        raise credentials_exception 
    
    return token_data # is a pydantic class TokenData, not a dictionary

def get_current_user(
        token: str = Depends(oauth_scheme),
        db: Session = Depends(get_db),
        ) -> Callable:
    

    credentials_exception_expiration_check = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Token has expired.',
        headers={'WWW-Authenticate': 'Bearer'},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
        )
    
    
    token_data = verify_access_token(token, credentials_exception, credentials_exception_expiration_check)

    # Verify that that the ID contained in the token is from a user that is registered 
    # in the database.
    db_session = DBSession(db, Users)
    user_credential = db_session.fetch_resource({'user_id': token_data.user_id})

    return user_credential