from datetime import timedelta, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the given user.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first offset number of rows
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def search_contact_by_name(contact_name: str, db: AsyncSession, user: User):
    """
    The search_contact_by_name function searches for a contact by name.
        Args:
            contact_name (str): The name of the contact to search for.
            db (AsyncSession): An async database session object.
            user (User): A User object representing the current user making this request.
    
    :param contact_name: str: Specify the name of the contact that you want to search for
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(name=contact_name, user=user)
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def search_contact_by_surname(contact_surname: str, db: AsyncSession, user: User):
    """
    The search_contact_by_surname function searches for a contact by surname.
        Args:
            contact_surname (str): The surname of the contact to search for.
            db (AsyncSession): An async database session object.
            user (User): A User object representing the current user making this request.
    
    :param contact_surname: str: Specify the contact surname to search for
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(surname=contact_surname, user=user)
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def search_contact_by_email(contact_email: str, db: AsyncSession, user: User):
    """
    The search_contact_by_email function searches for a contact by email.
        Args:
            contact_email (str): The email of the contact to search for.
            db (AsyncSession): An async database session object.
            user (User): A User object representing the current user making this request.
        Returns: 
            Contact or NoneType: If a matching Contact is found, it will be returned; otherwise, None will be returned.
    
    :param contact_email: str: Pass in the email of the contact we want to search for
    :param db: AsyncSession: Pass in the database session
    :param user: User: Get the user from the database
    :return: A single contact
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(email=contact_email, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def get_contact_by_birthday(n:int, db: AsyncSession, user: User):
    """
    The get_contact_by_birthday function takes in a number of days and returns all contacts with birthdays within that time frame.
        Args:
            n (int): The number of days to look ahead for birthdays.
            db (AsyncSession): An async session object from the SQLAlchemy library. This is used to query the database for contacts with birthdays within the specified time frame. 
            user (User): A User object representing a user in our database, which we use to filter out only those contacts belonging to this particular user when querying our database.
    
    :param n:int: Specify the number of days in the future to search for birthdays
    :param db: AsyncSession: Pass in the database session that will be used to query the database
    :param user: User: Filter the contacts by user
    :return: A list of contacts that have a birthday within the next n days
    :doc-author: Trelent
    """
    start = datetime.now()
    seven_days_later = start + timedelta(days=n)
    contacts_with_bdays = []

    stmt = select(Contact).filter_by(user=user).where(Contact.birthday != None)
    contacts = await db.execute(stmt)
    contacts = contacts.scalars().all()
    
    for contact in contacts:
        bday_this_year = datetime(year=start.year, 
                                  month=contact.birthday.month, 
                                  day=contact.birthday.day)

        if bday_this_year >= start and bday_this_year <= seven_days_later:
            contacts_with_bdays.append(contact)

    return contacts_with_bdays


async def get_contact(contact_id:int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact object from the database.
    
    :param contact_id:int: Filter the contact
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is only able to access their own contacts
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the user from the request
    :return: A contact object, which is a sqlalchemy model
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact



async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.phone_number = body.phone_number
        contact.email = body.email
        contact.birthday = body.birthday
        contact.notes = body.notes
        await db.commit()
        await db.refresh(contact)
    return contact
    


async def delete_contact(contact_id:int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact



  
