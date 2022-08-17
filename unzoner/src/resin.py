#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
from inspect import stack
from common import retry
from http.client import OK

from config import *


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def blink_leds():
    if not RESIN: return None

    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        '{}/v1/blink?apikey={}'.format(
            os.getenv('RESIN_SUPERVISOR_ADDRESS'),
            os.getenv('RESIN_SUPERVISOR_API_KEY')
        ),
        headers=headers,
        verify=REQUESTS_VERIFY,
        timeout=CONN_TIMEOUT
    )

    if DEBUG: print(res.status_code, res.content)

    if res.status_code not in [OK]:
        raise AssertionError((res.status_code, res.content))

    return (res.status_code, res.content.decode())
