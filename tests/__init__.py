import unittest
from app import app, db

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Setup the test client and initialize the database."""
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
        app.config['WTF_CSRF_ENABLED'] = False

        db.create_all()

    def tearDown(self):
        """Teardown the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
