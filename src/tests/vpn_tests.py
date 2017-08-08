from nose.tools import eq_, assert_is_not_none
from mock import patch

from vpn import get_openvpn_version, get_openvpn_binary


@patch('vpn.run_shell_cmd', return_value=(1, 'OpenVPN 2.4.3 x86_64-apple-darwin [SSL (OpenSSL)] [LZO] [LZ4] [PKCS11] [MH/RECVDA] [AEAD] built on Jun 21 2017...\n', '', 9204))
def test_get_openvpn_version_returns_correct_version(mock):
    result = get_openvpn_version()
    assert_is_not_none(result)
    eq_(result, '2.4.3')


@patch('vpn.run_shell_cmd', return_value=(0, '/usr/local/sbin/openvpn\n', '', 9352))
def test_get_openvpn_binary_not_none(mock):
    result = get_openvpn_binary()
    assert_is_not_none(result)
    eq_(result, '/usr/local/sbin/openvpn')
