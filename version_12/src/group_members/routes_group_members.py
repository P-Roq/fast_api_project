from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from src.oauth2 import get_current_user
from src.group_members.models_group_members import (
    GetGroupMember,
    GetGroupMemberShort,
    )
from src.database.db_setup import SessionLocal, get_db
from src.database.db_models import (
    Session,
    DBSession,
    GroupMembers,
    Users,
    )
from src.database.http_exceptions import (
    check_resource_availability,
    check_add_resource,
    check_object_availability,
    check_delete_resource,
    )

router = APIRouter()

@router.get(
    "/{group_id}",
    response_model=List[GetGroupMemberShort],
    )
def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSession(db, GroupMembers)

    user_resources = db_session.fetch_grouped_resources(
        id_column='group_id',
        id=group_id,
        )
    
    check_object_availability(user_resources, 'No posts were found.', 404)
    
    return user_resources


@router.get("/{group_id}/member/{user_id}", response_model=GetGroupMember,)
def get_group_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    ):

    # Membership info:
    db_session_members = DBSession(db, GroupMembers)
    
    resource_members = db_session_members.fetch_resource({'group_id': group_id, 'user_id': user_id}, False)
    
    check_object_availability(resource_members, f'Member {user_id} not found in social group {group_id}.', 404)

    # Member info.
    db_session_users = DBSession(db, Users)
    
    resource_user = db_session_users.fetch_resource({'user_id': user_id}, False)

    resource = {
        'member_id': resource_members.member_id,
        'group_id': resource_members.group_id,
        'user_id': resource_members.user_id,
        'name': resource_user.name,
        'email': resource_user.email,
        'admin': resource_members.admin,
        'total_posts': resource_members.total_posts,
        'created_at': resource_members.created_at,
        'updated_at': resource_members.updated_at,
    }

    return resource


@router.get("/", response_model=List[GetGroupMemberShort],)
def get_all_users_with_membership(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    search: Optional[str] = "",
    ):

    db_session = DBSession(db, GroupMembers)

    all_resources = db_session.all_resources(
        search_column='group_id',
        limit=limit,
        skip=skip,
        search=search,
        )

    check_object_availability(all_resources, 'No posts were found.', 404)
    
    return all_resources


# @router.post(
#     '/join/{group_id}',
#     status_code=status.HTTP_201_CREATED,
#     response_model=GetGroupMember,
#     )
@router.post(
    '/join/{group_id}',
    status_code=status.HTTP_201_CREATED,
    )
def post_group_member(
    group_id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    # group_id = resource.group_id
    user_id = credentials_user.user_id
   
    db_session = DBSession(db, GroupMembers)
    
    dump = {'group_id': group_id, 'user_id': user_id}

    current_resource = db_session.fetch_resource({'group_id': group_id,}, True)

    check_resource_availability(current_resource, f'Group {group_id} was not found.',)
    
    check_add_resource(lambda: db_session.add_resource(dump), 500) 
    
    resource = db_session.fetch_last_created 

    return resource



# @router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/leave/{group_id}",)
def delete_group_member(
    group_id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):


    user_id = credentials_user.user_id

    # Check social group.
    db_session_group = DBSession(db, GroupMembers)

    current_group = db_session_group.fetch_resource(
        {'group_id': group_id,},
        True
        )

    check_resource_availability(
        current_group,
        f'Group {group_id} was not found.',
        )

    # Check membership.
    db_session_members = DBSession(db, GroupMembers)

    user_id = credentials_user.user_id

    current_resource = db_session_members.fetch_resource(
        {'group_id': group_id, 'user_id': user_id},
        True
        )

    check_resource_availability(
        current_resource,
        f'User {user_id} is not a member of group {group_id}.',
        )
    
    # Check delete not working: it deletes, but it cannot recognize when noting is deleted.
    # Check deletes works fine for every other 'routes' script.
    check_delete_resource(
        lambda: db_session_members.delete_resource({'group_id': group_id, 'user_id': user_id}),
        f'User {user_id} is not a member of group {group_id}.',
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        )