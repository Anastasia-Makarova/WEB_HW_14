import unittest
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, date

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema
from src.repository.contacts import (get_contacts, 
                                     get_contact, 
                                     search_contact_by_name, 
                                     search_contact_by_surname, 
                                     search_contact_by_email, 
                                     get_contact_by_birthday, 
                                     create_contact, update_contact, 
                                     delete_contact)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password='a1d2m3', confirmed=True)
        self.session=AsyncMock(spec=AsyncSession)
        # self.today = datetime(2024, 3, 1)
        # self.date_mock = MagicMock()
        
    
    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, 
                            name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday=datetime(year=1998, month=6, day=3),
                            notes='note_1'),
                    Contact(id=2, 
                            name='test_name_2', 
                            surname='test_surname_2',
                            phone_number='+380502222222',
                            email='testmail2@mail.com',
                            birthday=datetime(year=1987, month=3, day=4),
                            notes='note_2')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)


    async def test_search_contact_by_name(self):
        contact = [Contact(id=1, 
                            name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday='2000-08-03',
                            notes='note_1')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contact
        self.session.execute.return_value = mocked_contacts
        result = await search_contact_by_name(contact_name='test_name_1', user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_search_contact_by_surname(self):
        contact = [Contact(id=1, 
                            name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday='2000-08-03',
                            notes='note_1')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contact
        self.session.execute.return_value = mocked_contacts
        result = await search_contact_by_surname(contact_surname='test_surname_1', user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_search_contact_by_email(self):
        contact = Contact(id=1, 
                          name='test_name_1', 
                          surname='test_surname_1',
                          phone_number='+380501111111',
                          email='testmail1@mail.com',
                          birthday='2000-08-03',
                          notes='note_1')
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await search_contact_by_email(contact_email='testmail1@mail.com', user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_by_birthday(self):
        contacts = [
            Contact(id=1,
                    name='test_name_1',
                    surname='test_surname_1',
                    phone_number='+380501111111',
                    email='testmail1@mail.com',
                    birthday=datetime.strptime('1998-03-12', '%Y-%m-%d'),
                    notes='note_1'),
            Contact(id=2,
                    name='test_name_2',
                    surname='test_surname_2',
                    phone_number='+380502222222',
                    email='testmail2@mail.com',
                    birthday=datetime.strptime('1987-03-17', '%Y-%m-%d'),
                    notes='note_2')
        ]

        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_birthday(n=7, db=self.session, user=self.user)
        self.assertEqual(result, contacts)
            

    async def test_get_contact(self):
        contact = Contact(id=1, 
                          name='test_name_1', 
                          surname='test_surname_1',
                          phone_number='+380501111111',
                          email='testmail1@mail.com',
                          birthday='2000-08-03',
                          notes='note_1')
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_create_contact(self):
        body = ContactSchema(name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday='2000-08-03',
                            notes='note_1')
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)

    
    async def test_update_contact(self):
        body = ContactSchema(id=1,
                            name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday='2000-08-03',
                            notes='note_1')
        mocked_contact = MagicMock( )
        mocked_contact.scalar_one_or_none.return_value = Contact(
                            id=1, 
                            name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday='2000-08-03',
                            notes='note_1',
                            user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)


    async def test_delete_contact(self):
        mocked_contact = MagicMock( )
        mocked_contact.scalar_one_or_none.return_value = Contact(
                            id=1, 
                            name='test_name_1', 
                            surname='test_surname_1',
                            phone_number='+380501111111',
                            email='testmail1@mail.com',
                            birthday='2000-08-03',
                            notes='note_1',
                            user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)
