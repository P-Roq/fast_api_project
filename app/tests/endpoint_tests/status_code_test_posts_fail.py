import os
import sys
import re

full_path = os.path.dirname(os.path.abspath(__file__))

path = re.sub('/tests/endpoint_tests', '', full_path)

sys.path.append(path)

from fastapi.testclient import TestClient
import httpx
import pytest

from main import my_rest_api

@pytest.fixture
def client():
    return TestClient(my_rest_api)

# The credentials below belong to two different users in the database, '1' has posted posts,
# '2'. This allows to test the failed GET requests when a user does not have any posts. 

credentials_1 = {
            "grant_type": "password",
            "username": "sol_rosales@mymail.com",
            "password": "4xzXi6HRUR"
            }

credentials_2 = {
            "grant_type": "password",
            "username": "vera_goldberg@mymail.com",
            "password": "life_oh_life"
            }


@pytest.fixture
def token_1(client):
    """Token for user with posted comments."""

    token_response = client.post(
        "/login",
        data={
            "grant_type": "password",
            "username": "sol_rosales@mymail.com",
            "password": "4xzXi6HRUR"
            },
        )
    token_data = token_response.json()
    access_token = token_data["access_token"]
    
    assert token_response.status_code == 200
    return access_token

@pytest.fixture
def token_2(client):
    """Token for user without any posted comment."""

    token_response = client.post(
        "/login",
        data={
            "grant_type": "password",
            "username": "vera_goldberg@mymail.com",
            "password": "life_oh_life"
            },
        )
    token_data = token_response.json()
    access_token = token_data["access_token"]
    
    assert token_response.status_code == 200
    return access_token


#### From posts routes

# def test_get_all_posts(client, get_access_token):
#     response = client.get(
#         "/posts",
#         headers={"Authorization": f"Bearer {get_access_token}"},
#         params={"query_param": "test"},
#         )
#     assert response.status_code == 400

def test_get_users_posts(client, token_2):
    # User has no posts.
    response = client.get(
        "/posts/my_posts",
        headers={"Authorization": f"Bearer {token_2}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 404


def test_get_post(client, token_1):
    # Inexistent post.
    response = client.get(
        "/posts/1000",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 404


def test_post_post(client, token_1):
    # Missing field.
    response_1 = client.post(
        "/posts/",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "score": 1.0,
            "view_count": 1,
            }
        )
    assert response_1.status_code == 422

    # Extra field.
    response_2 = client.post(
        "/posts/",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "score": 111,
            "view_count": 1,
            "title": "unit test post post",
            "something": "something"
            }
        )
    assert response_2.status_code == 422

    # Invalid score (not between 0 and 10, both included).
    response_3 = client.post(
        "/posts/",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "score": 111,
            "view_count": 1,
            }
        )
    assert response_3.status_code == 422


def test_put_post(client, token_1):
    # Inexistent post.
    response = client.put(
        "/posts/1000",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "score": 8.0,
            "view_count": 6322,
            "title": "unit test put post",
            }
        )
    assert response.status_code == 404


def test_patch_post(client, token_1):
    # Patch all fields (it fails, a PUT request is required)
    response_1 = client.patch(
        "/posts/1",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "score": 8.0,
            "view_count": 6322,
            "title": "failed patch",
            }
        )
    assert response_1.status_code == 422
    
    # Inexistent post.
    response_2 = client.patch(
        "/posts/1000",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "view_count": 6322,
            }
        )
    assert response_2.status_code == 404

    # Inexistent field.
    response_3 = client.patch(
        "/posts/1000",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        json={
            "extra_field": 6322,
            }
        )
    assert response_3.status_code == 422


def test_delete_post(client, token_1):
    # Inexistent post.
    response = client.delete(
        f"/posts/1000",
        headers={"Authorization": f"Bearer {token_1}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 404


