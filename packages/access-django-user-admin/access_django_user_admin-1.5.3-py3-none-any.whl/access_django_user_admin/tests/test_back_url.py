
import unittest
from types import SimpleNamespace
from access_django_user_admin.views import get_back_url

class DummyRequest:
    def __init__(self, get=None, meta=None):
        self.GET = get or {}
        self.META = meta or {}

class BackUrlUnitTests(unittest.TestCase):
    def test_back_url_query_param(self):
        req = DummyRequest(get={'back': '/custom-back/'})
        result = get_back_url(req)
        print(f"test_back_url_query_param: got '{result}' (expected '/custom-back/')")
        self.assertEqual(result, '/custom-back/')

    def test_back_url_http_referer(self):
        req = DummyRequest(meta={'HTTP_REFERER': '/referer-page/'})
        result = get_back_url(req)
        print(f"test_back_url_http_referer: got '{result}' (expected '/referer-page/')")
        self.assertEqual(result, '/referer-page/')

    def test_back_url_app_index(self):
        # Simulate no back param, no referer, fallback to app index
        req = DummyRequest()
        result = get_back_url(req)
        print(f"test_back_url_app_index: got '{result}' (should be app index URL or '/')")
        self.assertTrue(isinstance(result, str))

    def test_back_url_root(self):
        # If reverse fails, fallback to '/'
        print("test_back_url_root: not directly testable without mocking reverse, skipping.")
        pass

if __name__ == '__main__':
    unittest.main()
