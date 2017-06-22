#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inspect import stack
from traceback import print_exc

from common import retry
from paypal import check_active_paypal_subscription, get_jwt_payload_from_paypal
from bitcoin import check_active_bitcoin_payment
from api import get_device_env_by_name
from utils import decode_jwt_payload

from config import (DEBUG, PAYPAL_SUBSCRIPTION_CHECK, BITCOIN_PAYMENT_CHECK,
                    PAIRED_DEVICES_FREE, POLICY_ROUTING_CHECK)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def auth_user(uid, pwd):
    if not (uid and pwd): return False  

    # paired device check
    if PAIRED_DEVICES_FREE:
        paired_device = None
        try:
            paired_device = get_device_env_by_name(guid=uid, name='PAIRED_DEVICE_GUID')
        except AttributeError as e:
            print repr(e)
            if DEBUG: print_exc()
        
        if DEBUG: print 'paired_device=%s device=%s' % (paired_device, uid)
        if paired_device: return True

    # policy routing check
    if POLICY_ROUTING_CHECK:
        try:
            as_nums = get_device_env_by_name(guid=uid, name='AS_NUMS')
        except AttributeError as e:
            print repr(e)
            if DEBUG: print_exc()

        if DEBUG: print 'as_nums=%s device=%s' % (as_nums, uid)
        if as_nums and '#' in as_nums.split(' ') : return False
        
    # password check (resin.io devices)
    tun_passwd = None
    try:
        tun_passwd = get_device_env_by_name(guid=uid, name='TUN_PASSWD')
    except Exception as e:
        print repr(e)
        if DEBUG: print_exc()

    # password check (DD-WRT or Tomato routers)
    payload = None
    if not tun_passwd:
        try:
            payload = get_jwt_payload_from_paypal(baid=uid)
        except Exception as e:
            print repr(e)
            if DEBUG: print_exc()

        if payload:
            try:
                tun_passwd = decode_jwt_payload(encoded=payload)['p']
            except Exception as e:
                print repr(e)
                if DEBUG: print_exc()

    if not pwd == tun_passwd: return False

    # PayPal subscription check
    if PAYPAL_SUBSCRIPTION_CHECK:
        paypal = None
        baid = None
        if payload: baid = uid
        try:
            paypal = check_active_paypal_subscription(guid=uid, baid=baid)
        except Exception as e:
            print repr(e)
            if DEBUG: print_exc()
            
        if DEBUG: print 'paypal=%s device=%s' % (paypal, uid)
        if paypal: return True
    
    # Bitcoin payment check (resin.io devices)
    if BITCOIN_PAYMENT_CHECK:
        bitcoin = None
        try:
            bitcoin = check_active_bitcoin_payment(guid=uid)
        except Exception as e:
            print repr(e)
            if DEBUG: print_exc()
            
        if DEBUG: print 'bitcoin=%s device=%s' % (bitcoin, uid)
        if bitcoin: return True

    return False # deny ALL by default
