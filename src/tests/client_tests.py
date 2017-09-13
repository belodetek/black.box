from nose.tools import eq_, assert_is_not_none
from mock import patch
from uuid import uuid4
import imp

from client import connect_disconnect


@patch('client.plugin_loader.plugin.client_connect', return_value=True)
def test_client_connect(mock):
    result = connect_disconnect(cmd='connect', username=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, True)


@patch('client.plugin_loader.plugin.client_disconnect', return_value=True)
def test_client_disconnect(mock):
    result = connect_disconnect(cmd='disconnect', username=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, True)


def test_invalid_command():
    result = connect_disconnect(cmd='badcommand', username=uuid4().get_hex())
    assert_is_not_none(result)
    eq_(result, False)
