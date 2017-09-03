#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inspect import stack
from traceback import print_exc

from common import retry
from paypal import check_active_paypal_subscription, get_jwt_payload
from bitcoin import check_active_bitcoin_payment
from api import get_device_env_by_name
from utils import decode_jwt_payload

from config import (DEBUG, PAYPAL_SUBSCRIPTION_CHECK, BITCOIN_PAYMENT_CHECK,
                    PAIRED_DEVICES_FREE, POLICY_ROUTING_CHECK)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def auth_user(uid, pwd):
    if not (uid and pwd): return False
    uid = uid[:32]
    pwd = pwd[:16]

    # paired device check
    if PAIRED_DEVICES_FREE:
        try:
            paired_device = get_device_env_by_name(\
                guid=uid, name='PAIRED_DEVICE_GUID')
        except Exception as e:
            paired_device = None
        
        if DEBUG: print 'paired_device=%r uid=%r' % (paired_device, uid)
        if paired_device: return True

    # policy routing check (resin.io devices)
    if POLICY_ROUTING_CHECK:
        try:
            as_nums = get_device_env_by_name(guid=uid, name='AS_NUMS')
        except Exception as e:
            as_nums = None

        if DEBUG: print 'as_nums=%r uid=%r' % (as_nums, uid)
        if as_nums and '#' in as_nums.split() : return False
        
    # password check (resin.io Data API)
    jwtoken = None
    device_type = None
    try:
        tun_passwd = get_device_env_by_name(guid=uid, name='TUN_PASSWD')[:16]
        assert tun_passwd
    except Exception as e:
        # authenticate against JWT recorded against PayPal billing agreement
        try:
            jwtoken = decode_jwt_payload(encoded=get_jwt_payload(baid=uid))
            tun_passwd = jwtoken['p'][:16]
            device_type = jwtoken['t']
        except Exception as e:
            tun_passwd = None

    # deny all other devices with policy routing test enabled
    if POLICY_ROUTING_CHECK:
        if device_type and not device_type == 'RESIN':
            if DEBUG: print 'device_type=%r uid=%r' % (device_type, uid)
            return False

    if not tun_passwd: return False
    if not tun_passwd == pwd: return False

    # PayPal subscription check
    if PAYPAL_SUBSCRIPTION_CHECK:
        baid = None
        if jwtoken: baid = uid
        try:
            paypal = check_active_paypal_subscription(guid=uid, baid=baid)
        except Exception as e:
            paypal = None
            
        if DEBUG: print 'paypal=%s uid=%s' % (paypal, uid)
        if paypal: return True
    
    # Bitcoin payment check (resin.io Data API)
    if BITCOIN_PAYMENT_CHECK:
        try:
            bitcoin = check_active_bitcoin_payment(guid=uid)
        except Exception as e:
            bitcoin = None
            
        if DEBUG: print 'bitcoin=%s uid=%s' % (bitcoin, uid)
        if bitcoin: return True

    return False # deny ALL by default


def client_connect(uname):
    return True


def client_disconnect(uname):
    return True
