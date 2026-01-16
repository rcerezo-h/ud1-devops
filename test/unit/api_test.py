import unittest
import pytest

from app.api import api_application


@pytest.mark.unit
class TestApiRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = api_application.test_client()

    def test_hello_root(self):
        res = self.client.get("/")
        self.assertEqual(200, res.status_code)
        self.assertEqual(b"Hello from The Calculator!\n", res.data)

    def test_add_ok(self):
        res = self.client.get("/calc/add/1/2")
        self.assertEqual(200, res.status_code)
        self.assertEqual(b"3", res.data)

    def test_add_bad_request_invalid_number(self):
        res = self.client.get("/calc/add/a/2")
        self.assertEqual(400, res.status_code)
        self.assertTrue(len(res.data) > 0)

    def test_substract_ok(self):
        res = self.client.get("/calc/substract/10/6")
        self.assertEqual(200, res.status_code)
        self.assertEqual(b"4", res.data)

    def test_substract_bad_request_invalid_number(self):
        res = self.client.get("/calc/substract/a/2")
        self.assertEqual(400, res.status_code)
        self.assertTrue(len(res.data) > 0)
