from nose.tools import ok_, eq_, assert_is_not_none
from mock import patch, Mock
from http.client import OK
import requests

from gen_hash import generate_hash_key
from resin import blink_leds
from config import *


def test_generate_hash_key_returns_not_none():
    result = generate_hash_key()
    assert_is_not_none(result)


@patch('api.requests.post')
def test_blink_leds_returns_ok(mock_post):
    if not RESIN: return True
    mockresponse = Mock()
    mock_post.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content.data = 'OK'
    response = blink_leds()
    assert_is_not_none(response)
    eq_(response[0], OK)
    eq_(response[1].data, 'OK')
