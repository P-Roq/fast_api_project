import os
import sys
import re

full_path = os.path.dirname(os.path.abspath(__file__))

path = re.sub('/tests/authentication_tests', '', full_path)

sys.path.append(path)

from fastapi.testclient import TestClient
import httpx
import pytest

from main import my_rest_api


@pytest.fixture
def client():
    return TestClient(my_rest_api)

def test_login(client):
    # Test valid login.
    response = client.post(
        "/login",
        data={"username": "vera_goldberg@mymail.com", "password": "life_oh_life"}
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    # Test invalid login credentials.
    response = client.post(
        "/login",
        data={"username": "invalid_user", "password": "invalid_password"}
        )
    assert response.status_code == 403

def test_login_missing_credentials(client):
    # Test missing login credentials.
    response = client.post(
        "/login",
        data={}
        )
    assert response.status_code == 422 
