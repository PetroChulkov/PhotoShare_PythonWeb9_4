import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import PhotoRating, Photo, User
from src.schemas.rating import *

from src.repository.rating import (
    create_rating,
    update_avg_photo_rating,
    get_rating_by_id,
    remove_rating,
    get_rating
)


class TestRating(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.photo = Photo(id=1, rated_by=[])

    async def test_create_rating(self):
        body = PhotoRatingModel(photo_id=self.photo.id, rating=5)
        result = await create_rating(photo=self.photo, body=body, user=self.user, db=self.session)
        self.assertEqual(result.photo_id, body.photo_id)
        self.assertEqual(result.rating, body.rating)

    async def test_get_rating(self):
        ratings = [PhotoRating(), PhotoRating(), PhotoRating()]
        self.session.query(PhotoRating).limit().offset().all.return_value = ratings
        result = await get_rating(10, 0, self.session)
        self.assertEqual(result, ratings)

    async def test_get_rating_by_id_found(self):
        rating = PhotoRating()
        self.session.query(PhotoRating).filter_by().first.return_value = rating
        result = await get_rating_by_id(1, self.session)
        self.assertEqual(result, rating)

    async def test_get_rating_by_id_not_found(self):
        self.session.query(PhotoRating).filter_by().first.return_value = None
        result = await get_rating_by_id(1, self.session)
        self.assertIsNone(result)

    async def test_remove_rating_found(self):
        rating = PhotoRating()
        self.session.query(PhotoRating).filter_by().first.return_value = rating
        result = await remove_rating(1, self.session)
        self.assertEqual(result, rating)

    async def test_remove_rating_not_found(self):
        self.session.query(PhotoRating).filter_by().first.return_value = None
        result = await remove_rating(1, self.session)
        self.assertIsNone(result)
