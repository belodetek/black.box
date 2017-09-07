#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from inspect import stack
from traceback import print_exc

import vpn, nuitka
from common import retry
from config import (MAX_CONNS_SERVER, MAX_CONNS_CLIENT, DEBUG, DNS_SUB_DOMAIN,
                    USER_AUTH_ENABLED)

try:
    plugin = __import__('plugin')
except ImportError:
    plugin = None
    pass


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def authenticate(username=None, password=None):
    # user auth disabled completely (anything goes)
    if not USER_AUTH_ENABLED:
        print '%s: plugin=%s user_auth_enabled=%d username=%s password=%s authenticated' \
              % (stack()[0][3], DNS_SUB_DOMAIN,
                 USER_AUTH_ENABLED, username, password)
        return True

    # check number of server connections
    try:
        conns = vpn.get_server_conns()
    except Exception:
        conns = 0

    if conns > MAX_CONNS_SERVER:
        print '%s: plugin=%s username=%s server_conns=%s/%s' \
              % (stack()[0][3], DNS_SUB_DOMAIN, username, conns, MAX_CONNS_SERVER)
        return False

    # check number of client connections
    try:
        conns = vpn.get_client_conns(user=username)
    except Exception:
        conns = 0

    if conns > MAX_CONNS_CLIENT:
        print '%s: plugin=%s username=%s client_conns=%s/%s' \
              % (stack()[0][3], DNS_SUB_DOMAIN, username, conns, MAX_CONNS_CLIENT)
        return False

    # auth plug-ins
    result = False
    
    if plugin and 'auth_user' in dir(plugin):
        result = plugin.auth_user(username, password)
        if result:
            print '%s: plugin=%s user_auth_enabled=%d username=%s password=%s authenticated' \
                  % (stack()[0][3], DNS_SUB_DOMAIN, USER_AUTH_ENABLED,
                     username, password)
            return True

    print '%s: plugin=%s user_auth_enabled=%d username=%s password=%s authentication failed' \
          % (stack()[0][3], DNS_SUB_DOMAIN, USER_AUTH_ENABLED,
             username, password)
    return False


if __name__ == '__main__':
    try:
        username = os.getenv('username')
        passwd = os.getenv('password')
        result = authenticate(username=username, password=passwd)
    except Exception as e:
        result = None
    if result: sys.exit(0)
    sys.exit(1)
