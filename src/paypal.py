#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
from inspect import stack
from common import retry
from config import DEBUG, GUID

from api import (get_device_env_by_name, get_paypal_billing_agreement,
                 get_jwt_payload_from_paypal)

from httplib import (NO_CONTENT, UNAUTHORIZED, BAD_REQUEST, NOT_FOUND, OK,
                     FORBIDDEN)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_paypal_billing_agreement_id_for_guid(guid=None):
    try:
        result = get_device_env_by_name(\
            guid=guid, name='PAYPAL_BILLING_AGREEMENT')
    except:
        result = None
    return result


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def check_active_paypal_subscription(guid=GUID, baid=None):
    if not baid and not guid: return False
    if not baid:
        # try to obtain billing agreement id from resin.io
        baid = get_paypal_billing_agreement_id_for_guid(guid=guid)
        if not baid: return False
    
    # billing agreement id passed directly as username
    result = get_paypal_billing_agreement(baid=baid)
    if result:
        payload = json.loads(result)
        if payload['agreement_state'] in ['active']: return baid
    return False


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_jwt_payload(baid=None):
    if not baid: return None
    try:
        result = json.loads(\
            get_jwt_payload_from_paypal(baid=baid))['description'] 
    except:
        result = None
    return result
