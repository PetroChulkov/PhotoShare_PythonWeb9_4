import unittest
from unittest.mock import MagicMock
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from src.database.models import Photo, User, Role, Tag
from src.repository import tags as repository_tags
from src.schemas.photos import DescriptionUpdate, PhotoDb, TagResponse, PhotoSearch

from src.repository.tags import create_tags_for_photo


class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_create_tags_for_photo(self):
        result = await create_tags_for_photo(tags=['str', 'str'], db=self.session)
        self.assertIsInstance(result, list)

    async def test_create_tags_for_photo_amount(self):
        with self.assertRaises(HTTPException):
            await create_tags_for_photo(tags=['str', 'str', 'str', 'str', 'str', 'str'], db=self.session)

    async def test_create_tags_for_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await create_tags_for_photo(tags=['str', 'str'], db=self.session)
        self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()