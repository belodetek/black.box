from nose.tools import eq_, assert_is_not_none
from mock import patch
from uuid import uuid4

from auth import authenticate


@patch('auth.vpn.get_server_conns', return_value=0)
@patch('auth.plugin.auth_user', return_value=True)
def test_authenticate_user_success(mock_conns, mock_auth):
    result = authenticate(username=uuid4().get_hex(), password='secret')
    assert_is_not_none(result)
    eq_(result, True)


@patch('auth.vpn.get_server_conns', return_value=0)
@patch('auth.plugin.auth_user', return_value=False)
def test_authenticate_user_fail_username_password_wrong(mock_conns, mock_auth):
    result = authenticate(username=uuid4().get_hex(), password='wrong')
    assert_is_not_none(result)
    eq_(result, False)


@patch('auth.vpn.get_server_conns', return_value=100)
@patch('auth.plugin.auth_user', return_value=True)
def test_authenticate_user_fail_max_conns_reached(mock_conns, mock_auth):
    result = authenticate(username=uuid4().get_hex(), password='secret')
    assert_is_not_none(result)
    eq_(result, False)
