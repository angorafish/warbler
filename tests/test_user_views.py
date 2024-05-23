import os
from unittest import TestCase
from models import db, User, Follows, Likes, Message
from app import app, CURR_USER_KEY

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

class UserViewsTestCase(TestCase):
    """Test cases for user views."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user1 = User.signup("testuser1", "test1@test.com", "password", None)
        self.user2 = User.signup("testuser2", "test2@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        """Clean up any failed transactions."""
        db.session.rollback()

    def test_following_logged_in(self):
        """Can a logged-in user see the following page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/users/{self.user1.id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Following", str(resp.data))

    def test_following_logged_out(self):
        """Are logged-out users disallowed from seeing the following page?"""
        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_message_logged_in(self):
        """Can a logged-in user add a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.post("/messages/new", data={"text": "This is a test message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("This is a test message", str(resp.data))

    def test_add_message_logged_out(self):
        """Are logged-out users prohibited from adding messages?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "This is a test message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_delete_message_logged_in(self):
        """Can a logged-in user delete their own message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            msg = Message(text="This is a test message", user_id=self.user1.id)
            db.session.add(msg)
            db.session.commit()

            resp = c.post(f"/messages/{msg.id}/delete", folow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("This is a test message", str(resp.data))

    def test_delete_message_logged_out(self):
        """Are logged-out users prohibited from deleting messages?"""
        with self.client as c:
            msg = Message(text="This is a test message", user_id=self.user1.id)
            db.session.add(msg)
            db.session.commit()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_delete_message_other_user(self):
        """Are logged in users prohibited from deleting another user's message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            msg = Message(text="This is a test message", user_id=self.user2.id)
            db.session.add(msg)
            db.session.commit()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_user_likes_page(self):
        """Can we see the user's likes page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.index
            resp = c.get(f"/users/{self.u1.id}/likes")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Liked Warbles", str(resp.data))