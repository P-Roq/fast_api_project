from typing import List

from fastapi import (
    Path,
    APIRouter,
    Response,
    status,
    Depends
    )
from src.utils import capitalize_names, hash_pw
from src.users.models_users import PostUser, GetUser, PatchUser
from src.database.db_setup import get_db
from src.database.db_models import Session, DBSessionUsers
from src.oauth2 import get_current_user
from src.database.http_exceptions import (
    check_user_id_authorization,
    check_object_availability,
    check_add_resource,
    check_partial_fields,
    check_delete_resource,
    )

router = APIRouter()

@router.get("/id/{id}", response_model=GetUser)
def get_user_by_id(
    id: int, db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):
    
    db_session = DBSessionUsers(db)
    
    user_info = db_session.fetch_user_info('user_id', credentials_user.user_id,)
    
    check_object_availability(user_info, f'The user {id} was not found.', 404)

    return user_info


@router.get("/name/{name}", response_model=GetUser)
def get_user_by_name(
    name: str = Path(...), min_length=2, max_length=50,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):
    
    db_session = DBSessionUsers(db)

    name = capitalize_names(name)

    user_info = db_session.fetch_user_info('name', name,)
   
    check_object_availability(user_info, f'The user {name} was not found.', 404)

    return user_info

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=GetUser,
    )
def post_user(
    resource: PostUser,
    db: Session = Depends(get_db),
    ):

    db_session = DBSessionUsers(db)

    resource_dump = resource.model_dump()

    resource_dump['password'] = hash_pw(resource_dump['password'])

    check_add_resource(lambda: db_session.add_resource(resource_dump), 400)

    resource = db_session.fetch_last_created

    return resource


@router.put("/id/{id}")
def put_user(
    id: int,
    resource: PostUser,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionUsers(db)

    check_user_id_authorization(id, credentials_user.user_id)

    resource_dump = resource.model_dump()

    resource_dump['password'] = hash_pw(resource_dump['password'])

    check_add_resource(
        lambda: db_session.update_resource('user_id', id, resource_dump),
        500,
        )
    
    return Response(
            status_code=status.HTTP_200_OK,
            content=f'Post with ID {id} successfully updated.'
            )


@router.patch("/id/{id}")
def patch_user(
    id: int,
    resource: PatchUser,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionUsers(db)

    check_user_id_authorization(id, credentials_user.user_id)

    partial_resource_dump = resource.model_dump()
    partial_resource_dump = {key: partial_resource_dump[key] for key in partial_resource_dump if partial_resource_dump[key]}

    input_fields = partial_resource_dump.keys()
    required_fields = PatchUser.__annotations__.keys()
    check_partial_fields(input_fields, required_fields)

    if 'password' in partial_resource_dump:
        partial_resource_dump['password'] = hash_pw(partial_resource_dump['password'])

    check_add_resource(
        lambda: db_session.update_resource('user_id', id, partial_resource_dump),
        500,
        )
    
    return Response(
            status_code=status.HTTP_200_OK,
            content=f'Post with ID {id} successfully patched.'
            )


@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionUsers(db)

    check_user_id_authorization(id, credentials_user.user_id)
    
    check_delete_resource(
        lambda: db_session.delete_resource({'user_id': id}),
        f'User with ID {id} was not found.',
        )
    
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        )


@router.delete("/name/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_name(
    name: str = Path(...), min_length=2, max_length=50,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionUsers(db)

    name = capitalize_names(name)

    user_id = db_session.fetch_value_by_unique_value('name', 'user_id', name)

    check_user_id_authorization(user_id, credentials_user.user_id)

    check_delete_resource(
        lambda: db_session.delete_resource({'name': name}),
        f'User {name} was not found.',
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        )