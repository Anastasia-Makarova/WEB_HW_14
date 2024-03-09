from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema



async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.
    
    :param email: str: Get the email from the request body
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
        It takes a UserSchema object as input and returns the newly created user.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Inject the database session into the function
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession = Depends(get_db)):
    """
    The update_token function updates the refresh_token of a user.
        Args:
            user (User): The User object to update.
            token (str | None): The new refresh_token for the User object. If None, then no change is made to the current value of refresh_token in the database.
    
    :param user: User: Identify the user that is being updated
    :param token: str | None: Store the refresh token in the database
    :param db: AsyncSession: Pass in the database session
    :return: Nothing, but the function is decorated with @router
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a user as confirmed in the database.
    
    :param email: str: Get the email of the user
    :param db: AsyncSession: Pass in the database session
    :return: None, but we want to return the user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.
    
    :param email: str: Get the user from the database
    :param url: str | None: Specify the new avatar url
    :param db: AsyncSession: Pass in the database session to use
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(email: str, new_password: str, db: AsyncSession) -> User:
    """
    The update_password function updates the password of a user.
    
    :param email: str: Get the user by email
    :param new_password: str: Pass in the new password that will be set for the user
    :param db: AsyncSession: Pass a database session to the function
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.password = new_password
    await db.commit()
    await db.refresh(user)
    return user
