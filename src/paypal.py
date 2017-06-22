#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
from pprint import pprint
from inspect import stack
from common import retry
from config import (DEBUG, API_HOST, API_VERSION, API_SECRET, GUID)

from httplib import (NO_CONTENT, UNAUTHORIZED, BAD_REQUEST, NOT_FOUND, OK,
                     FORBIDDEN)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def check_active_paypal_subscription(guid=GUID, baid=None):
    headers = {'X-Auth-Token': API_SECRET}

    if not baid:
        # obtain billing agreement id from resin.io
        result = requests.get('%s/api/v%s/device/%s/env/%s' \
                              % (API_HOST, API_VERSION,
                                 guid, 'PAYPAL_BILLING_AGREEMENT'),
                              headers=headers)

        if DEBUG:
            if DEBUG: print '%r: status_code=%r content=%r' % (stack()[0][3],
                                                               result.status_code, result.content)

        if result.status_code in [OK]:
            baid = result.content
        else:
            return False
    
    # billing agreement id passed as username (DD-WRT and Tomato routers)
    result = requests.get('%s/api/v%s/paypal/billing-agreements/%s/confirm' \
                          % (API_HOST, API_VERSION, baid),
                          headers=headers)

    if DEBUG: print '%r: status_code=%r content=%r' % (stack()[0][3],
                                                       result.status_code,
                                                       result.content)

    if result.status_code in [OK]:
        payload = json.loads(result.content)
        if payload['agreement_state'] in ['active']: return baid

    return False


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_jwt_payload_from_paypal(baid=None):
    jwt_payload = None
    if not baid: return jwt_payload
    
    headers = {'X-Auth-Token': API_SECRET}
    result = requests.get('%s/api/v%s/paypal/billing-agreements/%s' \
                          % (API_HOST, API_VERSION, baid),
                          headers=headers)

    if DEBUG: print '%r: status_code=%r content=%r' % (stack()[0][3],
                                                       result.status_code,
                                                       result.content)

    if result.status_code in [OK]:
        jwt_payload = json.loads(result.content)['description']

    return jwt_payload
