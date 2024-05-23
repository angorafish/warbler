"""User model tests."""

import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user1 = User.signup("testuser1", "test1@test.com", "password", None)
        self.user2 = User.signup("testuser2", "test2@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        """Clean up any failed transaction."""
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
        user = User.signup(None, "test4@test.com", "password", None)
        with self.assertRaises(Exception):
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

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        self.assertFalse(self.u1.is_following(self.u2))