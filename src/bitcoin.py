#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, requests
from datetime import datetime, timedelta
from inspect import stack
from common import retry
from config import (DEBUG, API_HOST, API_VERSION, API_SECRET, GUID)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def check_active_bitcoin_payment(guid=GUID):
    headers = {'X-Auth-Token': API_SECRET}
    result = requests.get('%s/api/v%s/device/%s/env/%s' % (API_HOST, API_VERSION,
                                                           guid, 'BITCOIN_LAST_PAYMENT_DATE'),
                          headers=headers)

    if DEBUG: print '%s: %s' % (stack()[0][3], result)

    last_payment_date = None
    if result.status_code in [200]:
        last_payment_date = result.content

    result = requests.get('%s/api/v%s/device/%s/env/%s' % (API_HOST, API_VERSION,
                                                           guid, 'BITCOIN_LAST_PAYMENT_AMOUNT'),
                          headers=headers)

    if DEBUG: print '%s: %s' % (stack()[0][3], result)

    last_payment_amount = None
    if result.status_code in [200]:
        last_payment_amount = float(result.content)

    result = requests.get('%s/api/v%s/device/%s/env/%s' % (API_HOST, API_VERSION,
                                                           guid, 'BITCOIN_DAILY_AMOUNT'),
                          headers=headers)

    if DEBUG: print '%s: %s' % (stack()[0][3], result)

    btc_price = None
    if result.status_code in [200]:
        btc_price = float(result.content)

    expires = None
    if last_payment_date and last_payment_amount and btc_price:
        expires = datetime.strptime(last_payment_date, '%Y-%m-%dT%H:%M:%SZ') + timedelta(days=last_payment_amount / btc_price)
        if datetime.today() <= expires: return True

    return False
