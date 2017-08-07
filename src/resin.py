#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, requests
from inspect import stack
from common import retry
from httplib import OK

from config import DEBUG, RESIN


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def blink_leds():
    if not RESIN: return None
    
    headers = {'Content-Type': 'application/json'}
    res = requests.post('%s/v1/blink?apikey=%s' \
                        % (os.getenv('RESIN_SUPERVISOR_ADDRESS'),
                           os.getenv('RESIN_SUPERVISOR_API_KEY')),
                        headers=headers)

    if DEBUG: print res.status_code, res.content

    if res.status_code not in [OK]:
        raise AssertionError((res.status_code, res.content))

    return (res.status_code, res.content)
