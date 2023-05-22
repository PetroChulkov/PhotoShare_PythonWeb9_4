import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Comment, User
from src.schemas import CommentDb, CommentModel, CommentResponseModel, EditCommentModel

from src.repository.comments import (
    create_comment,
    get_comment,
    update_comment,
    remove_comment
)


class TestComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_create_comment(self):
        user_id = User.id
        body = CommentModel(
            comment="test",
            photo_id=1
        )
        result = await create_comment(body=body, db=self.session, user_id=user_id)
        self.assertEqual(result.comment, body.comment)
        self.assertTrue(hasattr(result, 'id'))

    async def test_get_comment_found(self):
        comment = Comment()
        self.session.query().filter().first.return_value = comment
        result = await get_comment(comment_id=1, db=self.session)
        self.assertEqual(result, comment)

    async def test_get_comment_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_comment(comment_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_remove_comment_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_comment(comment_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_update_comment(self):
        body = EditCommentModel(comment_id=1, edited_comment="test")
        comment = Comment()
        self.session.query().filter().first.return_value = comment
        self.session.commit.return_value = None
        result = await update_comment(body=body, db=self.session)
        self.assertEqual(result, comment)

    async def test_update_comment_not_found(self):
        body = EditCommentModel(comment_id=1, edited_comment="test")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_comment(body=body, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
