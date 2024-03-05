from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.config.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT, 
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Homework 13",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str): 
    """
    The send_email function sends an email to the user with a link to verify their email address.
        Args:
            email (str): The user's email address.
            username (str): The username of the user who is registering for an account. 
                This will be used in the body of the message sent to them, so they know which account it is for.
        host (str): The hostname that this application is running on, e.g., &quot;localhost&quot; or &quot;127.0.0.2&quot;. 
    
    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the email template
    :param host: str: Pass in the hostname of the server
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)

 