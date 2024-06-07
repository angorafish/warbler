import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes
from tests import BaseTestCase
from app import app

# Set an environmental variable to use a different database for tests
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

class UserModelTestCase(BaseTestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        super().setUp()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        self.user1 = User.signup("testuser1", "test1@test.com", "password", None)
        self.user2 = User.signup("testuser2", "test2@test.com", "password", None)
        db.session.commit()

    def tearDown(self):
        """Clean up any failed transaction."""
        super().tearDown()
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """Does the repr method work as expected?"""
        self.assertEqual(repr(self.user1), f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>")

    def test_is_following(self):
        """Does is_following detect when user1 is following user?"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        """Does is_followed_by detect when user1 is followed by user2?"""
        self.user2.following.append(self.user1)
        db.session.commit()

        self.assertTrue(self.user1.is_followed_by(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))

    def test_user_signup(self):
        """Does User.signup successfully create a new user if given valid credentials?"""
        user = User.signup("testuser3", "test3@test.com", "password", None)
        db.session.commit()

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser3")
        self.assertEqual(user.email, "test3@test.com")
        self.assertNotEqual(user.password, "password")

    def test_user_signup_fail(self):
        """Does User.signup fail to create a new user if any of the validations fail?"""
        with self.assertRaises(Exception):
            User.signup(None, "test4@test.com", "password", None)
            db.session.commit()

    def test_authenticate(self):
        """Does User.authenticate successfully return a user when given valid credentials?"""
        user = User.authenticate("testuser1", "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser1")

    def test_authenticate_fail(self):
        """Does User.authenticate fail to return a user when credentials are invalid?"""
        self.assertFalse(User.authenticate("wrongusername", "password"))
        self.assertFalse(User.authenticate("testuser1", "wrongpassword"))

    def test_likes_relationship(self):
        """Test the likes relationship between User and Message."""
        msg = Message(text="Test message", user_id=self.user2.id)
        db.session.add(msg)
        db.session.commit()

        like = Likes(user_id=self.user1.id, message_id=msg.id)
        db.session.add(like)
        db.session.commit()

        self.assertEqual(len(self.user1.likes), 1)
        self.assertEqual(self.user1.likes[0].message_id, msg.id)

    def test_follow_user(self):
        """Can a user follow another user?"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertTrue(self.user2.is_followed_by(self.user1))

    def test_unfollow_user(self):
        """Can a user unfollow another user?"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))

        self.user1.following.remove(self.user2)
        db.session.commit()

        self.assertFalse(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))

    def test_unique_email_constraint(self):
        """Does creating a user with a duplicate email address raise an exception?"""
        with self.assertRaises(Exception):
            duplicate_user = User.signup("testuser_duplicate", "test1@test.com", "password", None)
            db.session.commit()

    def test_unique_username_constraint(self):
        """Does creating a user with duplicate username raise an exception?"""
        with self.assertRaises(Exception):
            duplicate_user = User.signup("testuser1", "duplicate@test.com", "password", None)
            db.session.commit()

if __name__ == '__main__':
    import unittest
    unittest.main()
