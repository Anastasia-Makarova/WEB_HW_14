import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from src.repository.users import (get_user_by_email, create_user, update_token,
                                   confirmed_email, update_avatar_url, update_password)
from src.entity.models import User
from src.schemas.user import UserSchema
from src.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):

    async def test_get_user_by_email(self):
        email = 'test@example.com'
        user = User(id=1, email=email)
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        session = MagicMock(spec=AsyncSession)
        session.execute.return_value = mocked_user

        result = await get_user_by_email(email, session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body=UserSchema(
            username='test_user',
            email='test@mail.com',
            password='a1d2m3'
        )
        avatar_url = 'https://example.com/avatar.png'
        mocked_gravatar = MagicMock()
        mocked_gravatar.get_image.return_value = avatar_url

        with unittest.mock.patch('src.repository.users.Gravatar', return_value=mocked_gravatar):
            session = MagicMock(spec=AsyncSession)
            created_user = await create_user(body, session)
            self.assertEqual(created_user.email, body.email)
            self.assertEqual(created_user.avatar, avatar_url)

    async def test_update_token(self):
        user = User(id=1, email='test@example.com')
        token = 'test_token'
        session = MagicMock(spec=AsyncSession)

        await update_token(user, token, session)
        self.assertEqual(user.refresh_token, token)
        session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = 'test@mail.com'
        user = User(id=1, email=email)
        session = MagicMock(spec=AsyncSession)
        session.commit.return_value = None
        mocked_get_user_by_email = AsyncMock(return_value=user)

        with patch('src.repository.users.get_user_by_email', mocked_get_user_by_email):
            await confirmed_email(email, session)

        mocked_get_user_by_email.assert_called_once_with(email, session)
        user.confirmed = True
        session.commit.assert_called_once()

    async def test_update_avatar_url(self):
        email = 'test@example.com'
        new_avatar_url = 'https://example.com/new_avatar.png'
        user = User(id=1, email=email)
        session = MagicMock(spec=AsyncSession)
        session.commit.return_value = None
        mocked_get_user_by_email = AsyncMock(return_value=user)

        with patch('src.repository.users.get_user_by_email', mocked_get_user_by_email):
            updated_user = await update_avatar_url(email, new_avatar_url, session)

        mocked_get_user_by_email.assert_called_once_with(email, session)
        self.assertEqual(updated_user.avatar, new_avatar_url)
        session.commit.assert_called_once()

    async def test_update_password(self):
        email = 'test@example.com'
        new_password = 'new_password'
        user = User(id=1, email=email)
        session = MagicMock(spec=AsyncSession)
        session.commit.return_value = None
        mocked_get_user_by_email = AsyncMock(return_value=user)

        with patch('src.repository.users.get_user_by_email', mocked_get_user_by_email):
            await update_password(email, new_password, session)

        mocked_get_user_by_email.assert_called_once_with(email, session)
        self.assertEqual(user.password, new_password)
        session.commit.assert_called_once()