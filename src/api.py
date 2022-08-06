#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import urllib.parse

from inspect import stack
from common import retry
from traceback import print_exc
from http.client import OK, NO_CONTENT

from config import *


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_jwt_payload_from_paypal(baid=None):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/paypal/billing-agreements/{}'.format(
            API_HOST,
            API_VERSION,
            baid
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_paypal_billing_agreement(baid=None):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/paypal/billing-agreements/{}/confirm'.format(
            API_HOST,
            API_VERSION,
            baid
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_node_by_country(family=AF):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    country = urllib.parse.quote(TARGET_COUNTRY)
    if GEOIP_OVERRIDE:
        print('override={}'.format(GEOIP_OVERRIDE))
        country = GEOIP_OVERRIDE
    res = requests.get(
        '{}/api/v{}/node/{}/country/{}'.format(
            API_HOST,
            API_VERSION,
            family,
            country
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_node_by_guid(family=AF, guid=PAIRED_DEVICE_GUID):
    if not guid: return None
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/node/{}/guid/{}'.format(
            API_HOST,
            API_VERSION,
            family,
            guid
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content.decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_device_env_by_name(guid=GUID, name=None, default=None):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/device/{}/env/{}'.format(
            API_HOST,
            API_VERSION,
            guid,
            name
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content.decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_alpha(country):
    if not country: country = TARGET_COUNTRY
    country = urllib.parse.quote(country)
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/country/{}'.format(
            API_HOST,
            API_VERSION,
            country
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content.decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_guid_by_public_ipaddr(ipaddr=None, family=4):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/ipaddr/{}/{}'.format(
            API_HOST,
            API_VERSION,
            ipaddr,
            str(family)
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content.decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def put_device(family=AF, data=None, guid=GUID):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.put(
        '{}/api/v{}/device/{}/{}/{}'.format(
            API_HOST,
            API_VERSION,
            DEVICE_TYPE,
            guid,
            family
        ),
        data=json.dumps(data),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content.decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def dequeue_speedtest(guid=GUID):
    result = False
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.head(
        '{}/api/v{}/speedtest/{}'.format(
            API_HOST,
            API_VERSION,
            guid
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [NO_CONTENT]: result = True
    return result


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def update_speedtest(guid=GUID, data=None):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.patch(
        '{}/api/v{}/speedtest/{}'.format(
            API_HOST,
            API_VERSION,
            guid
        ),
        data=json.dumps(data),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return res.content.decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def dequeue_iotest(guid=GUID):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.get(
        '{}/api/v{}/iotest/queue/{}'.format(
            API_HOST,
            API_VERSION,
            guid
        ),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    try:
        assert res.status_code in [OK]
        return int(res.content)
    except:
        return None


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def update_iotest(guid=GUID, data=None):
    headers = {
        'X-Auth-Token': API_SECRET
    }
    res = requests.patch(
        '{}/api/v{}/iotest/{}'.format(
            API_HOST,
            API_VERSION,
            guid
        ),
        data=json.dumps(data),
        headers=headers,
        verify=REQUESTS_VERIFY
    )
    if DEBUG: print(
        '{}: status_code={} content={}'.format(
            stack()[0][3],
            res.status_code,
            res.content
        )
    )
    if res.status_code in [OK]: return (res.status_code, res.content.decode())

