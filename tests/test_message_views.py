"""Message View tests."""


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

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

            resp = c.post(f"/,essages/{self.msg2.id}/unlike", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_like_message(self):
        """Can a logged in user like a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            msg = Message(text="Test message", user_id=self.u2.id)
            db.session.add(msg)
            db.session.commit()

            resp = c.post(f"/messages/{msg.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Warble liked!", str(resp.data))

            like = Like.query.filter_by(user_id=self.u1.id, message_id=msg.id).first()
            self.assertIsNotNone(like)