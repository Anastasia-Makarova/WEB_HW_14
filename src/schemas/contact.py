from typing import Optional
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    surname: str  = Field(min_length=3, max_length=50)
    phone_number: str
    email: EmailStr
    birthday: date
    notes: Optional[str] = None


class ContactResponse(ContactSchema):
    id: int = 1
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None
    
    model_config = ConfigDict(from_attributes = True)

    