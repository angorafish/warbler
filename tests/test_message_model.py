"""Test message model"""
import os
from unittest import TestCase
from models import db, User, Message, Like
from app import app

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

class MessageModelTestCase(TestCase):
    """Tesrt cases for Message model."""
    
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user = User.signup("testUser", "test@test.com", "password", None)
        db.session.commit()
        
    def tearDown(self):
        """Clean up any failed transactions."""
        db.session.rollback()

    def test_message_model(self):
        """Does this basic model work?"""
        msg = Message(
            text="This is a test message",
            user_id=self.user.id
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "This is a test message")
        self.assertEqual(self.user.messages[0].user_id, self.user.id)

    def test_message_likes(self):
        """Does the likes relationship work correctly?"""
        like = Like(user_id=self.u1.id, message_id=self.m1.id)
        db.session.add(like)
        db.session.commit()

        m = Message.query.get(self.m1.id)
        self.assertEqual(len(m.likes), 1)
        self.assertEqual(m.likes[0].user_id, self.u1.id)