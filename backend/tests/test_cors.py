import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class CorsDefaultsTests(unittest.TestCase):
    def setUp(self):
        self.original_origin = os.environ.get("CORS_ORIGIN")
        os.environ.pop("CORS_ORIGIN", None)
        import app as app_module

        self.app_module = importlib.reload(app_module)
        self.client = self.app_module.create_app().test_client()

    def tearDown(self):
        if self.original_origin is None:
            os.environ.pop("CORS_ORIGIN", None)
        else:
            os.environ["CORS_ORIGIN"] = self.original_origin

    def test_default_cors_origin_uses_local_frontend_origin(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://127.0.0.1:5500")
        self.assertEqual(response.headers["Access-Control-Allow-Credentials"], "true")


if __name__ == "__main__":
    unittest.main()
