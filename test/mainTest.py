import unittest
from flask import Flask
from flask.testing import FlaskClient
from Smodal.main import app

class TestMain(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        headers = response.headers
        self.assertIn('X-Replit-User-Id', headers)
        self.assertIn('X-Replit-User-Name', headers)
        self.assertIn('X-Replit-User-Roles', headers)
        self.assertIn('X-Replit-User-Bio', headers)
        self.assertIn('X-Replit-User-Profile-Image', headers)
        self.assertIn('X-Replit-User-Teams', headers)
        self.assertIn('X-Replit-User-Url', headers)

if __name__ == '__main__':
    unittest.main()