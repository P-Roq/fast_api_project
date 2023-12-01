from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status
    )
from src.votes.models_votes import PostVote
from src.database.db_setup import SessionLocal, get_db
from src.database.db_models import (
    Session,
    DBSession,
    Votes,
    )
from src.oauth2 import get_current_user
from src.database.http_exceptions import (
    check_add_resource,
    check_resource_availability,
    check_delete_resource,
    )

router = APIRouter()

@router.post('/',)
def post_vote(
    vote: PostVote,
    db: Session = Depends(get_db),
    credentials_user: int = Depends(get_current_user),
    ):

    db_session = DBSession(db, Votes)

    new_resource = {'post_id': vote.post_id, 'user_id': credentials_user.user_id}

    current_resource = db_session.fetch_resource(new_resource, convert_to_dict=True,)

    if vote.vote == 1:
        check_resource_availability(
            current_resource,
            f'User {credentials_user.user_id} already voted on post {vote.post_id}.',
            conflict=True
            )
        check_add_resource(lambda: db_session.add_resource(new_resource), 404)    
    
        return Response(
            status_code=status.HTTP_202_ACCEPTED,
            content='Successful upvote.'
            )


    if vote.vote == 0:
        check_resource_availability(
            current_resource,
            f'Post {vote.post_id} not found.',
            )
        
        check_delete_resource(lambda: db_session.delete_resource(new_resource), id)
    
        return Response(
            status_code=status.HTTP_202_ACCEPTED,
            content='Upvote removed.'
            )