#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
from pprint import pprint
from inspect import stack
from common import retry
from config import (DEBUG, API_HOST, API_VERSION, API_SECRET, GUID)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def check_active_paypal_subscription(guid=GUID):
    headers = {'X-Auth-Token': API_SECRET}
    baid = requests.get('%s/api/v%s/device/%s/env/%s' % (API_HOST, API_VERSION,
                                                         guid, 'PAYPAL_BILLING_AGREEMENT'),
                        headers=headers)

    if DEBUG:
        print baid.status_code
        pprint(baid.content)

    if baid.status_code in [200]:
        res = requests.get('%s/api/v%s/paypal/billing-agreements/%s/confirm' % (API_HOST,
                                                                                API_VERSION,
                                                                                baid.content),
                           headers=headers)

        if DEBUG:
            print res.status_code
            pprint(res.content)

        if res.status_code in [200]:
            payload = json.loads(res.content)
            if payload['agreement_state'] in ['active']: return baid.content

    return False
