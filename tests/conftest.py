import os
import asyncio

import pytest
import pytest_asyncio

os.environ['TESTING'] = 'True'

from alembic import command
from alembic.config import Config

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.entity.models import Base, User
from src.database.db import get_db, DatabaseSessionManager
from src.services.auth import auth_service
from src.config.config import config



SQLALCHEMY_DATABASE_URL = config.TEST_DB_URL
# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(autocommit=False, 
                                         autoflush=False, 
                                         expire_on_commit=False,
                                         bind=engine)

test_user = {"username": "user_1", "email": "user1@mail.com.com", "password": "a1d2m3"}
user_data = {"username": "user_2", "email": "user2@mail.com", "password": "a1d2m3"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(username=test_user["username"], 
                                email=test_user["email"], 
                                password=hash_password,
                                confirmed=True)
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest_asyncio.fixture()
async def get_email_token():
    token = auth_service.create_email_token(data={"sub": test_user["email"]})
    return token