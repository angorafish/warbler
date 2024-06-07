import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes
from app import app, CURR_USER_KEY
from tests import BaseTestCase

# Set an environmental variable to use a different database for tests
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Create all tables
db.create_all()

class MessageViewTestCase(BaseTestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        super().setUp()
        self.client = app.test_client()

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        self.user1 = User.signup("testuser1", "test1@test.com", "password", None)
        self.user2 = User.signup("testuser2", "test2@test.com", "password", None)
        db.session.commit()

        self.msg1 = Message(text="Message 1", user_id=self.user1.id)
        self.msg2 = Message(text="Message 2", user_id=self.user2.id)
        db.session.add(self.msg1)
        db.session.add(self.msg2)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        super().tearDown()
        db.session.rollback()

    def test_add_message_logged_in(self):
        """Can a logged-in user add a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post("/messages/new", data={"text": "New message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("New message", str(resp.data))

    def test_add_message_logged_out(self):
        """Are logged-out users prohibited from adding messages?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "New message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_add_message_as_another_user(self):
        """Are logged-in users prohibited from adding a message as another user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"/messages/new", data={"text": "Message as another user", "user_id": self.user2.id}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Message as another user", str(resp.data))
    
    def test_delete_message_logged_in(self):
        """Can a logged in user delete their own message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"/messages/{self.msg1.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Message 1", str(resp.data))

    def test_delete_message_logged_out(self):
        """Are logged out users prohibited from deleting messages?"""
        with self.client as c:
            resp = c.post(f"/messages/{self.msg1.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_delete_message_other_user(self):
        """Are logged in users prohibited from deleting another user's message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"/messages/{self.msg2.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_add_like(self):
        """Can a logged-in user like a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post(f"/messages/{self.msg2.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            like = Likes.query.filter_by(user_id=self.user1.id, message_id=self.msg2.id).first()
            self.assertIsNotNone(like)

    def test_add_like_logged_out(self):
        """Are logged out users prohibited from liking messages?"""
        with self.client as c:
            resp = c.post(f"/messages/{self.msg2.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))
    
    def test_remove_like(self):
        """Can a logged in user unlike a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            like = Likes(user_id=self.user1.id, message_id=self.msg2.id)
            db.session.add(like)
            db.session.commit()

            resp = c.post(f"/messages/{self.msg2.id}/unlike", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            like = Likes.query.filter_by(user_id=self.user1.id, message_id=self.msg2.id).first()
            self.assertIsNone(like)

    def test_remove_like_logged_out(self):
        """Are logged-out users prohibited from unliking messages?"""
        with self.client as c:
            like = Likes(user_id=self.user1.id, message_id=self.msg2.id)
            db.session.add(like)
            db.session.commit()

            resp = c.post(f"/messages/{self.msg2.id}/unlike", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_view_messages_logged_in(self):
        """Can a logged-in user view messages?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/users/{self.user1.id}/messages")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message 1", str(resp.data))
            self.assertIn("Message 2", str(resp.data))

    def test_view_messages_logged_out(self):
        """Can a logged-out user view messages?"""
        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}/messages")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message 1", str(resp.data))
            self.assertIn("Message 2", str(resp.data))

    def test_view_single_message(self):
        """Can a user view a single message?"""
        with self.client as c:
            resp = c.get(f"/messages/{self.msg1.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message 1", str(resp.data))

    def test_view_liked_message(self):
        """Can a user view a liked message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            like = Likes(user_id=self.user1.id, message_id=self.msg2.id)
            db.session.add(like)
            db.session.commit()

            resp = c.get(f"/messages/{self.msg2.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message 2", str(resp.data))
            self.assertIn("liked", str(resp.data))

    def test_view_messages_by_other_user(self):
        """Can a user view messages by another user?"""
        with self.client as c:
            resp = c.get(f"/users/{self.user2.id}/messages")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message 2", str(resp.data))

if __name__ == '__main__':
    import unittest
    unittest.main()
