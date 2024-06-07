import os
from unittest import TestCase
from models import db, User, Message, Likes
from app import app
from tests import BaseTestCase

# Set an environmental variable to use a different database for tests
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Create all tables
db.create_all()

class MessageModelTestCase(BaseTestCase):
    """Test cases for Message model."""

    def setUp(self):
        """Create test client, add sample data."""
        super().setUp()
        self.client = app.test_client()

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        self.user = User.signup("testUser", "test@test.com", "password", None)
        db.session.commit()

        self.m1 = Message(text="This is a test message", user_id=self.user.id)
        db.session.add(self.m1)
        db.session.commit()

    def tearDown(self):
        """Clean up any failed transactions."""
        super().tearDown()
        db.session.rollback()

    def test_message_model(self):
        """Does this basic model work?"""
        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "This is a test message")
        self.assertEqual(self.user.messages[0].user_id, self.user.id)

    def test_message_likes(self):
        """Does the likes relationship work correctly?"""
        u2 = User.signup("testUser2", "test2@test.com", "password", None)
        db.session.commit()

        like = Likes(user_id=u2.id, message_id=self.m1.id)
        db.session.add(like)
        db.session.commit()

        m = Message.query.get(self.m1.id)
        self.assertEqual(len(m.liked_by), 1)
        self.assertEqual(m.liked_by[0].id, u2.id)

    def test_message_creation_invalid_user(self):
        """Test creating a message with an invalid user ID."""
        with self.assertRaises(Exception):
            msg = Message(text="Invalid user message", user_id=9999)
            db.session.add(msg)
            db.session.commit()

    def test_like_own_message(self):
        """Test liking own message should not be allowed."""
        like = Likes(user_id=self.user.id, message_id=self.m1.id)
        db.session.add(like)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_message_deletion(self):
        """Test that deleting a message removes it from the database."""
        msg_id = self.m1.id
        db.session.delete(self.m1)
        db.session.commit()
        m = Message.query.get(msg_id)
        self.assertIsNone(m)

    def test_user_deletion_cascade(self):
        """Test that deleting a user also deletes their messages."""
        user_id = self.user.id
        db.session.delete(self.user)
        db.session.commit()
        m = Message.query.get(self.m1.id)
        u = User.query.get(user_id)
        self.assertIsNone(m)
        self.assertIsNone(u)

if __name__ == '__main__':
    import unittest
    unittest.main()
