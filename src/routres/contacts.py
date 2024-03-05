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


@router.get('/', response_model=list[ContactResponse], 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), 
                       offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db), 
                       user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts for the current user.
        The limit and offset parameters are used to paginate the results.
    
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Check if the limit is greater than or equal to 10
    :param le: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip before returning results
    :param ge: Specify a minimum value for the parameter
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get("/name", response_model=list[ContactResponse], 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contact_by_name(contact_name: str, 
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    """
    The search_contact_by_name function searches for a contact by name.
        Args:
            contact_name (str): The name of the contact to search for.
            db (AsyncSession, optional): An async database session object. Defaults to Depends(get_db).
            user (User, optional): A User object containing information about the current user's session. Defaults to Depends(auth_service.get_current_user).
        Returns:
            Contact: A Contact object containing information about the searched-for contact.
    
    :param contact_name: str: Search for a contact by name
    :param db: AsyncSession: Get the database connection from the dependency injection
    :param user: User: Get the user_id from the logged in user
    :return: A contact object, which is a dict
    :doc-author: Trelent
    """
    contact = await repository_contacts.search_contact_by_name(contact_name, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/surname", response_model=list[ContactResponse], 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contact_by_surname(contact_surname: str, 
                                    db: AsyncSession = Depends(get_db),
                                    user: User = Depends(auth_service.get_current_user)):
    """
    The search_contact_by_surname function searches for a contact by surname.
        Args:
            contact_surname (str): The surname of the contact to search for.
            db (AsyncSession, optional): An async database session object. Defaults to Depends(get_db).
            user (User, optional): A User object containing information about the current user's session. Defaults to Depends(auth_service.get_current_user).
        Returns:
            Contact: A Contact object containing information about the searched-for contact.
    
    :param contact_surname: str: Pass the surname of the contact to be searched
    :param db: AsyncSession: Pass the database connection to the repository layer
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contact = await repository_contacts.search_contact_by_surname(contact_surname, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/email", response_model=ContactResponse, 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contact_by_email(contact_email: str, 
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    """
    The search_contact_by_email function searches for a contact by email.
        Args:
            contact_email (str): The email of the contact to search for.
            db (AsyncSession, optional): An async database session object. Defaults to Depends(get_db).
            user (User, optional): A User object containing information about the current user's session. Defaults to Depends(auth_service.get_current_user).
    
    :param contact_email: str: Search for a contact by email
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.search_contact_by_email(contact_email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/birthday", response_model=list[ContactResponse], 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact_by_birthday(n: int = 7, 
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_birthday function returns a list of contacts with birthdays within the next n days.
        The default value for n is 7, but it can be changed by passing in an integer as a parameter.
    
    :param n: int: Specify the number of days from today to check for birthdays
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contact_by_birthday(n, db, user)
    if contacts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="There are no birthdays within the given period")
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact(contact_id: int, 
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by its id.
        If the user is not logged in, an HTTP 401 Unauthorized error will be returned.
        If the contact does not exist, an HTTP 404 Not Found error will be returned.
    
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post('/', response_model=ContactResponse, 
             status_code=status.HTTP_201_CREATED, 
             description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def create_contact(body: ContactSchema, 
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactSchema object as input, and returns the newly created contact.
    
    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user from the auth_service
    :return: The contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}', 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(body:ContactSchema, 
                         contact_id: int = Path(ge=1), 
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id, body and db as parameters.
        It returns the updated contact.
    
    :param body:ContactSchema: Validate the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user from the auth_service
    :return: A contactschema object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT, 
               description='No more than 1 requests per 20 sec',
               dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def delete_contact(contact_id: int = Path(ge=1), 
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): An async session for interacting with the database.
            user (User): The current user, as determined by auth_service's get_current_user function.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact


