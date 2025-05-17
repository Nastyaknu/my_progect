import unittest
from io import BytesIO
from app_logic import application, parse_cookies
from base import get_categories, get_products

class TestSimpleFunctions(unittest.TestCase):

    def test_parse_cookies(self):
        environ = {'HTTP_COOKIE': 'user=Anna; cart=1,2,3'}
        result = parse_cookies(environ)
        self.assertEqual(result['user'], 'Anna')
        self.assertEqual(result['cart'], '1,2,3')

    def test_get_categories(self):
        result = get_categories()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_products(self):
        result = get_products()
        self.assertIsInstance(result, list)

class TestWSGIApplication(unittest.TestCase):

    def test_homepage(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'wsgi.input': BytesIO()
        }
        status = []
        def start_response(s, h): status.append(s)
        result = b''.join(application(environ, start_response)).decode('utf-8')
        self.assertIn("200 OK", status[0])
        self.assertIn("Усі товари", result)
        self.assertIn("Кошик", result)

    def test_account_page_unauthenticated(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/account',
            'QUERY_STRING': '',
            'wsgi.input': BytesIO()
        }
        status = []
        def start_response(s, h): status.append(s)
        result = b''.join(application(environ, start_response)).decode('utf-8')
        self.assertIn("200 OK", status[0])
        self.assertIn("Вхід в акаунт", result)

    def test_register_page(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/register',
            'QUERY_STRING': '',
            'wsgi.input': BytesIO()
        }
        status = []
        def start_response(s, h): status.append(s)
        result = b''.join(application(environ, start_response)).decode('utf-8')
        self.assertIn("200 OK", status[0])
        self.assertIn("<form", result)
        self.assertIn("username", result)
        self.assertIn("password", result)

if __name__ == '__main__':
    unittest.main()
