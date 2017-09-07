from nose.tools import eq_, assert_is_not_none
from mock import patch
from uuid import uuid4

from auth import authenticate


@patch('auth.vpn.get_server_conns', return_value=10)
@patch('auth.vpn.get_client_conns', return_value=1)
@patch('auth.plugin.auth_user', return_value=True)
def test_authenticate_user_success(*args):
    result = authenticate(username=uuid4().get_hex(), password='secret')
    assert_is_not_none(result)
    eq_(result, True)


@patch('auth.vpn.get_server_conns', return_value=10)
@patch('auth.plugin.auth_user', return_value=False)
def test_authenticate_user_password_wrong(*args):
    result = authenticate(username=uuid4().get_hex(), password='wrong')
    assert_is_not_none(result)
    eq_(result, False)


@patch('auth.vpn.get_server_conns', return_value=1000)
@patch('auth.plugin.auth_user', return_value=True)
def test_authenticate_user_max_server_conns_reached(*args):
    result = authenticate(username=uuid4().get_hex(), password='secret')
    assert_is_not_none(result)
    eq_(result, False)


@patch('auth.vpn.get_client_conns', return_value=10)
@patch('auth.plugin.auth_user', return_value=True)
def test_authenticate_user_max_client_conns_reached(*args):
    result = authenticate(username=uuid4().get_hex(), password='secret')
    assert_is_not_none(result)
    eq_(result, False)
