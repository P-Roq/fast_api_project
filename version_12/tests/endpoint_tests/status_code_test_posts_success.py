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

@pytest.fixture
def get_access_token(client):
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


def test_get_all_posts(client, get_access_token):
    response = client.get(
        "/posts",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 200


def test_get_users_posts(client, get_access_token):
    response = client.get(
        "/posts/my_posts",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 200


def test_get_post(client, get_access_token):
    response = client.get(
        "/posts/1",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 200


def test_post_post(client, get_access_token):
    response = client.post(
        "/posts/",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        json={
            "score": 1.0,
            "view_count": 1,
            "title": "unit test post post",
            }
        )
    assert response.status_code == 201


def test_put_post(client, get_access_token):
    response = client.put(
        "/posts/1",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        json={
            "score": 8.0,
            "view_count": 6322,
            "title": "unit test put post",
            }
        )
    assert response.status_code == 200


def test_patch_post(client, get_access_token):
    response = client.patch(
        "/posts/1",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        json={
            "view_count": 6322,
            }
        )
    
    assert response.status_code == 200


def test_delete_post(client, get_access_token):
    to_delete = 214
    response = client.delete(
        f"/posts/{to_delete}",
        headers={"Authorization": f"Bearer {get_access_token}"},
        params={"query_param": "test"},
        )
    assert response.status_code == 204

