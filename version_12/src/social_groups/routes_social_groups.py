from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from src.oauth2 import get_current_user
from src.social_groups.models_social_groups import (
    PostCreateSocialGroup,
    GetSocialGroup,
    GetAllSocialGroups,
    )
from src.database.db_setup import SessionLocal, get_db
from src.database.db_models import (
    Session,
    DBSession,
    DBSessionUsers,
    DBSessionSocialGroups,
    GroupMembers,
    )
from src.database.http_exceptions import (
    check_object_availability,
    check_resource_availability,
    check_add_resource,
    check_user_id_authorization,
    check_uniqueness,
    check_delete_resource,
    )

router = APIRouter()


@router.get("/", response_model=List[GetAllSocialGroups],)
def get_all_social_groups(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    search: Optional[str] = "",
    ):

    db_session = DBSessionSocialGroups(db,)

    all_resources = db_session.all_social_groups()

    check_object_availability(all_resources, 'No social groups were found.', 404)
    
    return all_resources


@router.get("/my_social_groups", response_model=List[GetAllSocialGroups],)
def get_users_social_groups(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    search: Optional[str] = "",
    credentials_user: int = Depends(get_current_user),
    ):
    """Get the social groups that user is member of."""

    db_session = DBSessionSocialGroups(db,)
    users_groups = db_session.fetch_social_group_members(user_id=3)
    # all_resources = db_session.all_social_groups(
    #     filter_columns={'user_id': credentials_user.user_id}
    # )

    check_object_availability(users_groups, 'No social groups were found.', 404)
    
    return users_groups


@router.get("/{group_id}", response_model=GetSocialGroup,)
def get_social_group(
    group_id: int,
    db: Session = Depends(get_db),
    ):

    # Get group.
    db_session_group = DBSessionSocialGroups(db,)
    
    resource_group = db_session_group.fetch_resource({'group_id': group_id}, False)

    check_object_availability(resource_group, f'Group with ID {group_id} not found.', 404)

    # Get number of members.
    resource_group.members = db_session_group.count_members_by_social_group(group_id=group_id)
    
    # Get admin name.
    db_session_users = DBSessionUsers(db,)
    
    resource_user = db_session_users.fetch_resource({'user_id': resource_group.admin_id}, False)
    
    full_resource = {
        'group_id': resource_group.group_id, 
        'admin_id': resource_group.admin_id, 
        'admin_name': resource_user.name, 
        'title': resource_group.title, 
        'details': resource_group.details, 
        'created_at': resource_group.created_at, 
        'updated_at': resource_group.updated_at, 
        'members': resource_group.members,
        }

    return full_resource


@router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
    response_model=PostCreateSocialGroup,
    )
def post_social_group(
    resource: PostCreateSocialGroup,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    user_id = credentials_user.user_id

    post_dump = resource.model_dump()

    group_title = post_dump['title']

    post_dump['admin_id'] = user_id

    
    db_session_group = DBSessionSocialGroups(db,)

    # Check group.
    resource_group = db_session_group.fetch_resource({'title': group_title}, False)

    check_resource_availability(resource_group, f'Social Group {group_title} already exists.', conflict=True)
    
    # Add group.
    check_add_resource(lambda: db_session_group.add_resource(post_dump), 404) 
    
    current_resource = db_session_group.fetch_last_created
    
    # Add admin to group members.
    db_session_members = DBSession(db, GroupMembers)

    group_members_entry = {
        'user_id': user_id,
        'group_id': current_resource.group_id,
        'admin': True,
    }

    check_add_resource(lambda: db_session_members.add_resource(group_members_entry), 404) 

    
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=f'User {user_id} successfully created the social group {group_title}.'
        )


@router.post(
    '/join/{group_id}',
    status_code=status.HTTP_200_OK,
    response_model=PostCreateSocialGroup,
    )
def post_create_social_group(
    group_id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    user_id = credentials_user.user_id

    # Check group.
    db_session_group = DBSessionSocialGroups(db,)
    
    resource_group = db_session_group.fetch_resource({'group_id': group_id}, False)

    check_object_availability(resource_group, f'Social group with ID {group_id} was not found.', 404)

    # Add admin to group members.
    db_session_members = DBSession(db, GroupMembers)

    group_members_entry = {
        'user_id': user_id,
        'group_id': group_id,
    }

    check_add_resource(lambda: db_session_members.add_resource(group_members_entry), 404) 

    
    return Response(
        status_code=status.HTTP_200_OK,
        content=f'User {user_id} successfully joined social group with ID {group_id}.'
        )



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_social_group(
    id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSessionSocialGroups(db,)

    admin_id = db_session.fetch_value_by_unique_value('group_id', 'admin_id', id)

    check_user_id_authorization(admin_id, credentials_user.user_id)

    check_uniqueness(
        False, db_session.unique_values('group_id'), id, f'Social group with ID {id} was not found.',
        )
    
    check_delete_resource(
        lambda: db_session.delete_resource({'group_id': id}),
        f'Social group with ID {id} was not found.',
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        )

