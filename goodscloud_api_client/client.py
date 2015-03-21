"""
Usage:

# Instantiate with API host, username, and password:
>>> gc = GoodsCloudAPIClient(host="http://app.goodscloud.com", user="test@test.com", pwd="mypass")

# Then, do requests as follows:
>>> orders = gc.get(
>>>     "internal/order",
>>>     q=dict(filters=[dict(name="channel_id", op="eq", val=16)]), results_per_page=20, page=1)
200 OK
>>> first_id = orders.json()['objects'][0]['id']
>>> gc.patch(url="internal/order/{}".format(first_id),
>>>     dict(pay_later=True)
200 OK
>>> gc.delete(url="internal/order/{}".format(first_id))
204 NO CONTENT

# Instantiating a GoodsCloudAPIClient with debug=True provides output to debug
# authentication and request composition issues with partners.
"""

from base64 import b64encode
from hashlib import sha1, md5
import hmac
import json
import logging
import sys
import time
from functools import wraps
try:
    from urllib import urlencode, unquote_plus
except ImportError:
    from urllib.parse import urlencode, unquote_plus

import requests

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)


def request_wrapper(fn):
    """Function decorator executing common tasks for each request:

    * prepend path with /api/
    * make request
    * print response status code and reason

    """
    @wraps(fn)
    def wrap_request(self, path, *args, **kwargs):
        assert path.startswith(("/api/internal", "/api/external")), (
            "The provided URL path must start with `/api/internal` or `/api/external`."
        )
        resp = fn(self, path, *args, **kwargs)
        logger.info('{} {}'.format(resp.status_code, resp.reason))
        return resp
    return wrap_request


def jsonify_params(kwargs):
    """JSON-ifies & url-encodes all keyword arguments of type dict."""
    return urlencode({
        key: json.dumps(value) if type(value) == dict else value
        for (key, value) in kwargs.items()
    })


class GoodsCloudAPIClient(object):

    def __init__(self, host, user, pwd, version='current', debug=False, aws_credentials=False):
        self.host = host # Example: `https://app.goodscloud.com`
        self.user = user
        self.pwd = pwd
        session = self.login(self.user, self.pwd, aws_credentials)
        self.headers = {
            'Accept': 'application/json; version=%s' % (version,),
            'Authorization': session['access_token'],
        }
        self.debug = debug
        if self.debug is True:
            sys.settrace(debug_trace)

    def login(self, email, password, aws_credentials):
        headers = {"GC-Email": email, "GC-Password": password,}
        resp = requests.post(
            self.host + '/token',
            headers=headers,
            verify=False,
        )
        try:
            session = resp.json()
        except ValueError as exc:
            logger.critical(resp.request.url)
            logger.critical(resp.text)
            raise exc
        assert 'error' not in session, session
        return session


    def _post_patch_put(self, method, url, obj_dict, **kwargs):
        """Common steps for all methods which create or edit objects."""
        # Convert provided Python dictionary object into JSON
        body_data = json.dumps(obj_dict)
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        url = "{}{}?{}".format(self.host, path, jsonify_params(kwargs))
        return getattr(requests, method)(
            url,
            data=body_data,
            headers=headers,
        )

    @request_wrapper
    def get(self, path, **kwargs):
        if ('q' in kwargs and kwargs['q'].get('filters', None)
            or 'filters' in kwargs
        ):
            assert type(kwargs['q']['filters']) == list, (
                "Filters must be a list of dicts, wrapped within query parameter `q`."
            )
        url = "{}{}?{}".format(self.host, path, jsonify_params(kwargs))
        return requests.get(url, headers=self.headers)

    @request_wrapper
    def delete(self, url):
        signed_url = self._create_signed_url(url, 'DELETE')
        return requests.delete(signed_url, headers=self.headers)

    @request_wrapper
    def post(self, url, obj_dict, **kwargs):
        return self._post_patch_put('post', url, obj_dict, **kwargs)

    @request_wrapper
    def put(self, url, obj_dict, **kwargs):
        return self._post_patch_put('put', url, obj_dict, **kwargs)

    @request_wrapper
    def patch(self, url, obj_dict, **kwargs):
        return self._post_patch_put('patch', url, obj_dict, **kwargs)


def main():
    try:
        from IPython import embed
        embed(banner1='')
    except ImportError:
        from code import interact
        interact(local={'GoodsCloudAPIClient': GoodsCloudAPIClient})


if __name__ == "__main__":
    main()


# Seconds the request is valid. Useful for debugging purposes
EXPIRES = 500


def debug_trace(frame, event, arg):
    """Prints debug info. Used when GoodsCloudAPIClient.debug is set.
    Exists to keep the 'functional' code free of log clutter."""
    filename = frame.f_code.co_filename
    fnname = frame.f_code.co_name
    if filename.find("api_client.py") == -1:
        return debug_trace

    if fnname is 'create_query_params' and event == 'return':
        print("\n--- Query args:\n{}".format(arg))

    elif fnname is '_create_sign_str' and event == 'call':
        print("\n--- App secret:\n{}".format(
            frame.f_locals['self'].auth['app_secret']))
        print("\n--- Signature string input parameters: ")
        for (arg, val) in frame.f_locals.items():
            if arg == 'self': continue
            print("{}: {}".format(arg, val))

    elif fnname is "_sign" and event == 'call':
        print("\n--- Composed string to-be-signed:\n{}".format(
            repr(frame.f_locals['string'])))

    elif fnname is "_sign" and event == 'return':
        print("\n--- Resulting signature:\n{}".format(arg))

    elif fnname is '_create_signed_url' and event == 'return':
        url = frame.f_locals['url']
        print("\n--- Resulting URL:\n{}".format(url))
        print("\n--- Unquoted URL:\n{}".format(unquote_plus(url)))
    return debug_trace
