#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inspect import stack
from traceback import print_exc

from common import retry
from paypal import check_active_paypal_subscription
from bitcoin import check_active_bitcoin_payment
from api import get_device_env_by_name

from config import (DEBUG, PAYPAL_SUBSCRIPTION_CHECK, BITCOIN_PAYMENT_CHECK,
                    PAIRED_DEVICES_FREE, RESIN)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def auth_user(uid, pwd):
    if not (uid and pwd): return False

    # Paired device check
    if PAIRED_DEVICES_FREE:
        paired_device = get_device_env_by_name(guid=uid,
                                               name='PAIRED_DEVICE_GUID')
        
        if DEBUG: print 'paired_device=%s device=%s' % (paired_device, uid)
        if paired_device: return True

    if RESIN:
        # policy routing check
        as_nums = list()
        try:
            as_nums = get_device_env_by_name(guid=uid, name='AS_NUMS').split(' ')
        except AttributeError as e:
            pass

        if DEBUG: print 'as_nums=%s device=%s' % (as_nums, uid)

        if '#' in as_nums: return False

    # password check
    tun_passwd = None
    try:
        tun_passwd = get_device_env_by_name(guid=uid, name='TUN_PASSWD')
        assert tun_passwd
    except Exception as e:
        print repr(e)
        if DEBUG: print_exc()
        return False

    if not pwd == tun_passwd: return False
        
    # PayPal subscription check
    if PAYPAL_SUBSCRIPTION_CHECK:
        paypal = check_active_paypal_subscription(guid=uid)
        if DEBUG: print 'paypal=%s device=%s' % (paypal, uid)
        if paypal: return True
    
    # Bitcoin payment check
    if BITCOIN_PAYMENT_CHECK:
        bitcoin = check_active_bitcoin_payment(guid=uid)
        if DEBUG: print 'bitcoin=%s device=%s' % (bitcoin, uid)
        if bitcoin: return True

    return False # deny ALL by default
