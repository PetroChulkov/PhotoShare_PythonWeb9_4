import os
import sys

sys.path.append(os.path.abspath("."))

from datetime import datetime, date

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

import src
from src.database.models import User
from src.schemas import UserModel, UserPublic
from src.repository.users import (
    get_user_by_username,
    get_user_by_email,
    check_quantity_of_users,
    create_user,
    check_exist_username,
    to_ban_user,
    check_ban_status,
    get_user_profile,
    change_password,
    confirmed_email,
    check_exist_mail,
    update_token,
    search_by_mail,
)

# python -m unittest -v tests/test_unit_repository_users.py


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            user_name="Mike",
            email="testmike@test.com",
            password="qweasd",
            confirmed=False,
            ban_status=False,
            created_at=datetime(2022, 12, 5),
        )

    async def test_get_contact(self):
        user = self.user
        self.session.query().filter(user_name=user.user_name).first.return_value = user
        result = await get_user_by_username(username="Mike", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email(self):
        user = self.user
        self.session.query().filter(email=user.email).first.return_value = user
        result = await get_user_by_email(email="testmike@test.com", db=self.session)
        self.assertEqual(result, user)

    async def test_search_by_mail(self):
        user = self.user
        self.session.query().filter_by(email=user.email).first.return_value = user
        result = await search_by_mail(inquiry="testmike@test.com", db=self.session)
        self.assertEqual(result, user)

    async def test_check_exist_mail(self):
        body = UserModel(
            user_name="Mike",
            email="testmike@test.com",
            password="qweasd",
        )
        self.session.query().filter_by(email=body.email).first.return_value = body
        result = await check_exist_mail(body=body, db=self.session)
        self.assertEqual(result, body)

    async def test_check_exist_username(self):
        body = UserModel(
            user_name="Mike",
            email="testmike@test.com",
            password="qweasd",
        )
        self.session.query().filter_by(
            user_name=body.user_name
        ).first.return_value = body
        result = await check_exist_username(body=body, db=self.session)
        self.assertEqual(result, body)

    async def test_check_quantity_of_users(self):
        contacts = [User(), User, User()]
        self.session.query().all.return_value = contacts
        result = await check_quantity_of_users(db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_user(self):
        body = UserModel(
            user_name="Mike",
            email="testmike@test.com",
            password="qweasd",
        )
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.user_name, body.user_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_to_ban_user(self):
        body = UserModel(
            user_name="Mike",
            email="testmike@test.com",
            password="qweasd",
        )
        result = await to_ban_user(body=body, email=body.email, db=self.session)
        self.assertTrue(result.ban_status)

    async def test_confirmed_email(self):
        user = self.user
        result = await confirmed_email(email=user.email, db=self.session)
        self.assertTrue(result.confirmed)

    async def test_check_ban_status(self):
        user = self.user
        result = await check_ban_status(username=user.user_name, db=self.session)
        self.assertTrue(result)

    async def test_get_user_profile(self):
        user = self.user
        public_profile = UserPublic(
            user_name="Mike", created_at=user.created_at, photos_published=1
        )
        self.session.query().filter(username=user.user_name).first.return_value = user
        result = await get_user_profile(username=user.user_name, db=self.session)
        self.assertEqual(result, public_profile)

    async def test_update_token(self):
        token = "12345"
        user = User()
        user_refresh_token_before_update = user.refresh_token
        result = await update_token(user=user, token=token, db=self.session)
        self.assertNotEqual(user.refresh_token, user_refresh_token_before_update)

    async def test_change_password(self):
        user = self.user
        new_password = "kek"
        result = await change_password(
            user=user, new_password=new_password, db=self.session
        )
        self.assertEqual(user.password, new_password)


if __name__ == "__main__":
    unittest.main()
