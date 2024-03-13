from unittest.mock import Mock
import json

from requests import HTTPError

import pytest
from sqlalchemy import select
from tests.conftest import TestingSessionLocal, user_data
from fastapi import HTTPException

from src.entity.models import User
from src.schemas.user import UserSchema, RequestEmail
from src.config import messages
from fastapi.testclient import TestClient

# user_data = {"username": "test_user_2", "email": "test_mail_2@mail.com", "password": "a1d2m3"}



@pytest.fixture
def mock_send_email():
    return Mock()


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



def test_repeat_signup(client, monkeypatch, mock_send_email, capsys):
    try:
        monkeypatch.setattr("src.routres.auth.send_email", mock_send_email)
        with pytest.raises(HTTPException) as exc_info:
            client.post("api/auth/signup", json=user_data)
    except Exception as err:
        captured = capsys.readouterr()
        stdout_output = captured.out
        assert f"409: {messages.ACCOUNT_EXIST}" in stdout_output



# def test_not_confirmed_login(client):
#     response = client.post("api/auth/login",
#                            data={"username": user_data.get("email"), "password": user_data.get("password")})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == messages.EMAIL_NOT_CONFIRMED
    




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


    
# def test_wrong_login_password(client):
#     response = client.post("api/auth/login",
#                            data={"username": user_data.get("email"), "password": "idontknow"})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == messages.INVALID_PASSWORD


# def test_wrong_email_login(client):
#     response = client.post("api/auth/login",
#                            data={"username": "email@gmail.com", "password": user_data.get("password")})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == messages.INVALID_EMAIL
    

@pytest.mark.asyncio
async def test_confirmed_email(get_email_token, client): 
    token = get_email_token
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.EMAIL_ALREADY_CONFIRMED


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data



@pytest.mark.asyncio  
async def test_request_email(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = False
            await session.commit()        
        mock_send_email = Mock()
        monkeypatch.setattr("src.routres.auth.request_email", mock_send_email)
        response = client.post("api/auth/request_email", json=user_data)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == messages.CHECK_EMAIL
        assert "password" not in data


