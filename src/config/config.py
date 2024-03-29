from typing import Any
from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings
 


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:567234@localhost:5432/hw11db"
    TEST_DB_URL: str = "postgresql+asyncpg://postgres:567234@localhost:5432/testdb"
    SECRET_KEY_JWT: str = "12345serkertkey"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "name@meta.ua"
    MAIL_PASSWORD: str = "postgres"
    MAIL_FROM: str = "some company"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = "HW13"
    CLD_API_KEY: int = 834932673911364
    CLD_API_SECRET: str = "secret"


    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra="ignore", env_file = ".env", env_file_encoding = "utf-8")




config = Settings()
