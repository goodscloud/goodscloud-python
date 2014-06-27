import time
import unittest

import responses
from goodscloud_api_client.client import GoodsCloudAPIClient

def mock_time():
    return 1403771045.000000


class APIClientTest(unittest.TestCase):

    @responses.activate
    def test_login(self):
        responses.add(responses.POST, 'http://localhost:5000/session',
                          body='{"email": "user@example.com", "auth": {}}', status=200,
                          content_type='application/json')
        GoodsCloudAPIClient('http://localhost:5000', 'user@example.com', 'password')

    @responses.activate
    def test_unsuccessful_login(self):
        responses.add(responses.POST, 'http://localhost:5000/session',
                          body='{"email": null}', status=200,
                          content_type='application/json')
        with self.assertRaises(AssertionError) as context:
            GoodsCloudAPIClient('http://localhost:5000', 'user@example.com', 'wrongpassword')
        self.assertEqual(context.exception.message, 'Login failed on http://localhost:5000')

class AuthenticatedAPIClientTest(unittest.TestCase):
    @responses.activate
    def setUp(self):
        responses.add(responses.POST, 'http://localhost:5000/session',
            body='''{
                "email": "user@example.com",
                "auth": {
                    "app_key": "APPKEY",
                    "app_token": "APPTOKEN",
                    "app_secret": "APPSECRET"
                }
            }
            ''',
            status=200,
            content_type='application/json',
        )
        time.time = mock_time
        self.api = GoodsCloudAPIClient('http://localhost:5000', 'user@example.com', 'password')



    @responses.activate
    def test_get(self):
        responses.add(
            responses.GET,
            'http://localhost:5000/api/internal/channel_product',
            status=200,
            content_type='application/json',
        )
        res = self.api.get('/api/internal/channel_product')
        self.assertEquals(
            responses.calls[0].request.url,
            'http://localhost:5000/api/internal/channel_product?expires=2014-06-26T08%3A32%3A25Z&key=APPKEY&token=APPTOKEN&sign=gLC2KB8crSqbbiqFQwooCO5m4kU'
        )

    @responses.activate
    def test_get_with_filters(self):
        responses.add(
            responses.GET,
            'http://localhost:5000/api/internal/channel_product',
            status=200,
            content_type='application/json',
        )
        res = self.api.get('/api/internal/channel_product', q=dict(filters=[dict(channel_id=5)]))
        self.assertEquals(
            responses.calls[0].request.url,
            'http://localhost:5000/api/internal/channel_product?expires=2014-06-26T08%3A32%3A25Z&key=APPKEY&q=%7B%22filters%22%3A+%5B%7B%22channel_id%22%3A+5%7D%5D%7D&token=APPTOKEN&sign=pwA4WnxhZ%2B268VlBI%2FQcQdO%2Fp%2FA'
        )
