import unittest
from unittest.mock import MagicMock
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.models import Photo, User, Role, Tag
from src.repository import tags as repository_tags
from src.schemas import DescriptionUpdate, PhotoDb, TagResponse, PhotoSearch

from src.repository.photos import (
    get_all_photos,
    get_photo,
    remove_photo,
    update_description,
    search_photo_by_keyword,
    search_photo_by_tag,
    create_qr_code,
    upload_photo,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_all_photos(self):
        photos = [Photo()]
        self.session.query().offset().limit().all = photos
        result = await get_all_photos(offset=0, limit=1, db=self.session)
        self.assertTrue(hasattr(result, "id"))

    async def test_upload_photo(self):
        result = await upload_photo(user_id=int, src_url='test', description='test', tags=['test'], db=self.session)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_photo_found(self):
        photo = Photo()
        self.session.query().filter().first.return_value = photo
        result = await get_photo(photo_id=1, db=self.session)
        self.assertEqual(result, photo)

    async def test_get_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_photo(photo_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_remove_photo_found(self):
        photo = Photo()
        self.session.query().filter().first.return_value = photo
        result = await remove_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(result, photo)

    async def test_remove_photo_found_admin(self):
        photo = Photo()
        user = User(id=1, user_name='string', email='user@email.com', password='string', roles=Role.admin)
        self.session.query().filter().first.return_value = photo
        result = await remove_photo(photo_id=1, user=user, db=self.session)
        self.assertEqual(result, photo)


    async def test_remove_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_photo(photo_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_description(self):
        body = PhotoDb(id=1, photo="test", description="test surname", tags=[Tag(id=1, tag_name='test')], qr_code="test" )
        photo = Photo()
        self.session.query().filter().first.return_value = photo
        self.session.commit.return_value = None
        result = await update_description(photo_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, photo)

    async def test_update_description_admin(self):
        body = PhotoDb(id=1, photo="test", description="test surname", tags=[Tag(id=1, tag_name='test')], qr_code="test" )
        user = User(id=1, user_name='string', email='user@email.com', password='string', roles=Role.admin)
        photo = Photo()
        self.session.query().filter().first.return_value = photo
        self.session.commit.return_value = None
        result = await update_description(photo_id=1, body=body, user=user, db=self.session)
        self.assertEqual(result, photo)

    async def test_update_description_not_found(self):
        body = PhotoDb(id=1, photo="test", description="test surname", tags=[Tag(id=1, tag_name='test')], qr_code="test" )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_description(photo_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_photo_by_keyword_found(self):
        result = await search_photo_by_keyword(search_by="test", filter_by=None, db=self.session)
        print(result)
        self.assertTrue(result)

    async def test_search_photo_by_keyword_found_filter_creation_date(self):
        result = await search_photo_by_keyword(search_by="test", filter_by='creation_date', db=self.session)
        print(result)
        self.assertTrue(result)

    async def test_search_photo_by_keyword_found_filter_rating(self):
        result = await search_photo_by_keyword(search_by="test", filter_by='rating', db=self.session)
        print(result)
        self.assertTrue(result)

    async def test_search_photo_by_keyword_not_found(self):
        body = PhotoSearch(id=1, photo='test', qr_code='test', description='test', created_at=datetime.now(), tags=[Tag(id=1, tag_name='test')], average_rating=1.0)
        result = await search_photo_by_keyword(search_by="test", filter_by=None, db=self.session)
        self.assertNotEqual(result.photo, body.photo)

    async def test_search_photo_by_tag_found(self):
        result = await search_photo_by_tag(search_by="test", filter_by=None, db=self.session)
        print(result)
        self.assertTrue(result)

    async def test_search_photo_by_tag_not_found(self):
        body = PhotoSearch(id=1, photo='test', qr_code='test', description='test', created_at=datetime.now(), tags=[Tag(id=1, tag_name='test')], average_rating=1.0)
        result = await search_photo_by_tag(search_by="test", filter_by=None, db=self.session)
        self.assertNotEqual(result.photo, body.photo)

    async def test_search_create_qr_code(self):
        body = PhotoDb(id=1, photo='test', qr_code='test', description='test', tags=[Tag(id=1, tag_name='test')])
        result = await create_qr_code(photo_id=1, url='str', user=self.user, db=self.session)
        self.assertNotEqual(result.qr_code, body.qr_code)

    async def test_search_photo_by_tag_found_filter_creation_date(self):
        result = await search_photo_by_tag(search_by="test", filter_by='creation_date', db=self.session)
        print(result)
        self.assertTrue(result)

    async def test_search_photo_by_tag_found_filter_rating(self):
        result = await search_photo_by_tag(search_by="test", filter_by='rating', db=self.session)
        print(result)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()