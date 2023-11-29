from uvicorn import run

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.posts.routes_posts import router as posts_router
from src.users.routes_users import router as users_router
from src.votes.routes_votes import router as votes_router
from src.social_groups.routes_social_groups import router as social_groups_router
from src.group_members.routes_group_members import router as group_members_router
from src.auth.routes_auth import router as auth_router

from src.route_config import LOGIN_ROUTE

my_rest_api = FastAPI()

origins = [
    "http://127.0.0.1:8000",
]

my_rest_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Add CSP middleware to set Content-Security-Policy header.
# @my_rest_api.middleware("http")
# async def add_csp_header(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Content-Security-Policy"] = "default-src 'self' http://127.0.0.1:8000/favicon.ico"
#     return response

my_rest_api.include_router(posts_router, prefix='/posts', tags=['posts'])
my_rest_api.include_router(users_router, prefix='/users', tags=['users'])
my_rest_api.include_router(votes_router, prefix='/votes', tags=['votes'])
my_rest_api.include_router(social_groups_router, prefix='/social_groups', tags=['social_groups'])
my_rest_api.include_router(group_members_router, prefix='/group_members', tags=['group_members'])
my_rest_api.include_router(auth_router, prefix='/' + LOGIN_ROUTE, tags=['authentication'])


def main() -> None:
    run(
        'main:my_rest_api',
        host='127.0.0.1',
        port=8000,
        reload=True
        )

if __name__ == '__main__':
    main()      


