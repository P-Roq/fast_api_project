from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from src.oauth2 import get_current_user
from src.group_members.models_group_members import (
    GetGroupMemberShort_1,
    GetGroupMemberShort_2,
    )
from src.database.db_setup import SessionLocal, get_db
from src.database.db_models import (
    Session,
    DBSessionGroupMembers,
    )
from src.database.http_exceptions import (
    check_resource_availability,
    check_add_resource,
    check_object_availability,
    check_delete_resource,
    )

router = APIRouter()

@router.get("/{group_id}", response_model=List[GetGroupMemberShort_2],)
def get_all_members_by_group(
    group_id: int,
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    search: Optional[str] = "",
    ):

    db_session = DBSessionGroupMembers(db)

    members_by_group = db_session.get_all_members_by_group('group_id', group_id)

    check_object_availability(members_by_group, 'No posts were found.', 404)
    
    return members_by_group


@router.get("/{group_id}/{user_id}", response_model=GetGroupMemberShort_2,)
def get_group_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    ):
    
    db_session = DBSessionGroupMembers(db)

    members_by_group = db_session.get_all_members_by_group('group_id', group_id)

    check_object_availability(members_by_group, 'No posts were found.', 404)

    for member in members_by_group:
        if member['user_id'] == user_id:
            return member


@router.get("/", response_model=List[GetGroupMemberShort_1],)
def get_all_users_with_membership(
    db: Session = Depends(get_db),
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    search: Optional[str] = "",
    ):

    db_session = DBSessionGroupMembers(db)

    all_resources = db_session.all_resources(
        search_column='group_id',
        limit=limit,
        skip=skip,
        search=search,
        )

    check_object_availability(all_resources, 'No posts were found.', 404)
    
    return all_resources


@router.post(
    '/join/{group_id}',
    status_code=status.HTTP_201_CREATED,
    )
def join_group_member(
    group_id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    user_id = credentials_user.user_id
   
    db_session = DBSessionGroupMembers(db)
    
    dump = {'group_id': group_id, 'user_id': user_id}

    current_resource = db_session.fetch_resource({'group_id': group_id,}, True)

    check_resource_availability(current_resource, f'Group {group_id} was not found.',)
    
    check_add_resource(lambda: db_session.add_resource(dump), 500) 
    
    return Response(
        status_code=status.HTTP_201_CREATED,
        )



@router.delete("/leave/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(
    group_id: int,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):


    user_id = credentials_user.user_id

    # Check social group.
    db_session_group = DBSessionGroupMembers(db)

    current_group = db_session_group.fetch_resource(
        {'group_id': group_id,},
        True
        )

    check_resource_availability(
        current_group,
        f'Group {group_id} was not found.',
        )

    # Check membership.
    db_session_members = DBSessionGroupMembers(db)

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