from unittest.mock import Mock
import json

import pytest
from sqlalchemy import select
from tests.conftest import TestingSessionLocal

from src.entity.models import User
from src.schemas.user import UserSchema, RequestEmail
from src.config import messages

user_data = {"username": "test_user_2", "email": "test_mail_2@mail.com", "password": "a1d2m3"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr('src.routres.auth.send_email', mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert 'password' not in data
    assert 'avatar' in data
    assert mock_send_email.called
    # assert mock_send_email.call_count == 1


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routres.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


# def test_not_confirmed_login(client):
#     response = client.post("api/auth/login",
#                            data={"username": user_data.get("email"), "password": user_data.get("password")})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


    
# def test_wrong_password_login(client):
#     response = client.post("api/auth/login",
#                            data={"username": user_data.get("email"), "password": "password"})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == "Invalid password"


# def test_wrong_email_login(client):
    # response = client.post("api/auth/login",
#                            data={"username": "email", "password": user_data.get("password")})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == "Invalid email"


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

