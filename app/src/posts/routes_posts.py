from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from src.oauth2 import get_current_user
from src.posts.models_posts import (
    PatchPost,
    GetPost,
    GetAllPosts,
    PostPost,
    PutPost,
    )
from src.database.db_setup import SessionLocal, get_db
from src.database.db_models import (
    Session,
    DBSessionPosts,
    )
from src.database.http_exceptions import (
    check_object_availability,
    check_add_resource,
    check_user_id_authorization,
    check_uniqueness,
    check_partial_fields,
    check_delete_resource,
    )

router = APIRouter()

@router.get("/my_posts", response_model=List[GetAllPosts],)
def get_users_posts(
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):
    """Fetch logged in user's posts."""

    db_session = DBSessionPosts(db)

    user_resources = db_session.all_posts(
        filter_columns={'user_id': credentials_user.user_id},
        )
    
    check_object_availability(user_resources, 'No posts were found.', 404)
    
    return user_resources


@router.get("/{id}", response_model=GetPost,)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    ):

    db_session = DBSessionPosts(db)
    
    resource = db_session.fetch_resource({'post_id': id}, False)
    check_object_availability(resource, 'Post not found.', 404)

    resource.upvotes = db_session.get_upvotes_by_post(post_id=id)

    # Add a view.
    updated_view_count = resource.view_count + 1
    
    check_add_resource(
        lambda: db_session.update_resource(
            id_column='post_id',
            id=id,
            dump={'view_count': updated_view_count}
            ),
        status_code=500,
        )
    
    return resource


@router.get("/", response_model=List[GetAllPosts],)
def get_all_posts(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    search: Optional[str] = "",
    ):

    db_session = DBSessionPosts(db)
    
    all_resources = db_session.all_posts(
        limit=limit,
        skip=skip,
        search=search,
        )

    check_object_availability(all_resources, 'No posts were found.', 404)
    
    return all_resources


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=PostPost,
    )
def post_post(
    resource: PostPost,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionPosts(db)

    post_dump = resource.model_dump()

    post_dump['user_id'] = credentials_user.user_id

    check_add_resource(lambda: db_session.add_resource(post_dump), 404)
    
    resource = db_session.fetch_last_created
    
    return resource


@router.put("/{id}",)
def put_post(
    id: int,
    resource: PutPost,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionPosts(db)

    user_id = db_session.fetch_value_by_unique_value('post_id', 'user_id', id)

    check_user_id_authorization(user_id, credentials_user.user_id)

    resource_dump = resource.model_dump()

    check_uniqueness(
        False, db_session.unique_values('post_id'), id, f'Post {id} was not found.',
        )
    
    check_add_resource(
    lambda: db_session.update_resource('post_id', id, resource_dump),
    500,
    )
    
    return Response(
            status_code=status.HTTP_200_OK,
            content=f'Post with ID {id} successfully updated.'
            )


@router.patch("/{id}")
def patch_post(id: int,
    resource: PatchPost,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionPosts(db)

    user_id = db_session.fetch_value_by_unique_value('post_id', 'user_id', id)

    check_user_id_authorization(user_id, credentials_user.user_id)

    check_uniqueness(
        False, db_session.unique_values('post_id'), id, f'Post {id} was not found.',
        )

    partial_resource_dump = resource.model_dump()
    partial_resource_dump = {
        key: partial_resource_dump[key] for key in partial_resource_dump if partial_resource_dump[key]
        }
    
    input_fields = partial_resource_dump.keys()
    required_fields = PatchPost.__annotations__.keys()
    check_partial_fields(input_fields, required_fields)

    
    check_uniqueness(
        False, db_session.unique_values('post_id'), id, f'Post {id} was not found.',
        )
    
    check_add_resource(
    lambda: db_session.update_resource('post_id', id, partial_resource_dump),
    500,
    )
    
    return Response(
            status_code=status.HTTP_200_OK,
            content=f'Post with ID {id} successfully patched.'
            )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionPosts(db)

    user_id = db_session.fetch_value_by_unique_value('post_id', 'user_id', id)

    check_user_id_authorization(user_id, credentials_user.user_id)

    check_uniqueness(
        False, db_session.unique_values('post_id'), id, f'Post {id} was not found.',
        )
    
    check_delete_resource(
        lambda: db_session.delete_resource({'post_id': id}),
        f'Post {id} was not found.',
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        )

