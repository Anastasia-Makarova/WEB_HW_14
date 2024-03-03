from datetime import date

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.entity.models import User
from src.services.auth import auth_service
from src.database.db import get_db
from src.repository import contacts as repository_contacts
from src.schemas.contact  import ContactSchema, ContactResponse


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse], description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db), 
                       user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get("/name", response_model=list[ContactResponse], description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contact_by_name(contact_name: str, db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.search_contact_by_name(contact_name, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/surname", response_model=list[ContactResponse], description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contact_by_surname(contact_surname: str, db: AsyncSession = Depends(get_db),
                                    user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.search_contact_by_surname(contact_surname, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/email", response_model=ContactResponse, description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contact_by_email(contact_email: str, db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.search_contact_by_email(contact_email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/birthday", response_model=list[ContactResponse], description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact_by_birthday(n: int = 7, db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contact_by_birthday(n, db, user)
    if contacts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no birthdays within the given period")
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}', description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(body:ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT, description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact


