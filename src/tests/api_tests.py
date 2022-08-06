from nose.tools import ok_, eq_, assert_is_not_none
from mock import patch, Mock
from http.client import OK
from uuid import uuid4
import random, socket, struct, requests

from api import (
    get_node_by_country,
    get_node_by_guid,
    get_device_env_by_name,
    get_alpha,
    get_guid_by_public_ipaddr,
    put_device,
    dequeue_speedtest,
    update_speedtest
)


@patch('api.requests.get')
def test_get_node_by_country_returns_ipaddr(mock_get):
    ipaddr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    mockresponse = Mock()
    mock_get.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content.data = ipaddr
    response = get_node_by_country()
    assert_is_not_none(response)
    eq_(response.data, ipaddr)


@patch('api.requests.get')
def test_get_node_by_guid_returns_ipaddr(mock_get):
    ipaddr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    mockresponse = Mock()
    mock_get.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content = ipaddr.encode()
    response = get_node_by_guid(guid=uuid4().hex)
    assert_is_not_none(response)
    eq_(response, ipaddr)


@patch('api.requests.get')
def test_get_device_env_by_name_returns_ipaddr(mock_get):
    guid = uuid4().hex
    country = 'United States'
    mockresponse = Mock()
    mock_get.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content = country.encode()
    response = get_device_env_by_name(guid=guid, name='TARGET_COUNTRY')
    assert_is_not_none(response)
    eq_(response, country)


@patch('api.requests.get')
def test_get_alpha_returns_alpha2(mock_get):
    mockresponse = Mock()
    alpha2 = 'us'.encode()
    mock_get.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content = alpha2
    response = get_alpha('United States')
    assert_is_not_none(response)
    eq_(response, alpha2.decode())


@patch('api.requests.get')
def test_get_guid_by_public_ipaddr_returns_guid(mock_get):
    ipaddr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    guid = uuid4().hex
    mockresponse = Mock()
    mock_get.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content = guid.encode()
    response = get_guid_by_public_ipaddr(ipaddr=ipaddr)
    assert_is_not_none(response)
    eq_(response, guid)


@patch('api.requests.put')
def test_put_device_returns_data(mock_put):
    guid = uuid4().hex
    data = {'ip': '64.15.188.66', 'city': 'Chesterfield', 'country': 'United States'}
    res = '{\n  "auth": "None", \n  "bytesin": "None", \n  "bytesout": "None", \n  "cipher": "None", \n  "city": "Chesterfield", \n  "conns": "None", \n  "country": "United States", \n  "dt": "2017-08-06 13:46:46", \n  "guid": "e08b5c83f8da459e8e7ac90744c8c5be", \n  "hostapd": "None", \n  "id": 12385, \n  "ip": "64.15.188.66", \n  "proto": 4, \n  "status": "None", \n  "type": 2, \n  "upnp": "None"\n}\n'
    mockresponse = Mock()
    mock_put.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content = res.encode()
    response = put_device(guid=guid, data=data)
    assert_is_not_none(response)
    eq_(response, res)


@patch('api.requests.head')
def test_dequeue_speedtest_returns_false(mock_head):
    guid = uuid4().hex
    mockresponse = Mock()
    mock_head.return_value = mockresponse
    mockresponse.status_code = OK
    result = dequeue_speedtest(guid=guid)
    assert_is_not_none(result)
    eq_(result, False)


@patch('api.requests.patch')
def test_update_speedtest_returns_data(mock_patch):
    guid = uuid4().hex
    data = {'status': 1, 'down': None, 'up': None}
    result = '1\n'
    mockresponse = Mock()
    mock_patch.return_value = mockresponse
    mockresponse.status_code = OK
    mockresponse.content = result.encode()
    response = update_speedtest(guid=guid, data=data)
    assert_is_not_none(response)
    eq_(response, result)
