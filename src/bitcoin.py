#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, requests
from datetime import datetime, timedelta
from inspect import stack
from common import retry
from config import DEBUG, GUID
from api import get_device_env_by_name


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_last_payment_date(guid=None):
    try:
        result = get_device_env_by_name(\
            guid=guid, name='BITCOIN_LAST_PAYMENT_DATE')
    except:
        result = None
    return result


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_last_payment_amount(guid=None):
    try:
        result = get_device_env_by_name(\
            guid=guid, name='BITCOIN_LAST_PAYMENT_AMOUNT')
        if result: result = float(result)
    except:
        result = None
    return result


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_daily_amount(guid=None):
    try:
        result = get_device_env_by_name(\
            guid=guid, name='BITCOIN_DAILY_AMOUNT')
        if result: result = float(result)
    except:
        result = None
    return result


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def check_active_bitcoin_payment(guid=GUID):
    last_payment_date = get_last_payment_date(guid=guid)
    last_payment_amount = get_last_payment_amount(guid=guid)
    daily_amount = get_daily_amount(guid=guid)
    expires = None
    if last_payment_date and last_payment_amount and daily_amount:
        expires = datetime.strptime(last_payment_date, '%Y-%m-%dT%H:%M:%SZ') \
                  + timedelta(days=last_payment_amount / daily_amount)
        if datetime.today() <= expires: return True
    return False
