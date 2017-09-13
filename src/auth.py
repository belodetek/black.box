#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from inspect import stack
from traceback import print_exc

from common import retry
import vpn, plugin_loader

from config import (MAX_CONNS_SERVER, MAX_CONNS_CLIENT, DEBUG, DNS_SUB_DOMAIN,
                    USER_AUTH_ENABLED)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def authenticate(username=None, password=None):
    # bypass auth
    if not USER_AUTH_ENABLED:
        print '{0}: plugin={1} user_auth_enabled={2} username={3}'.\
              format(stack()[0][3], DNS_SUB_DOMAIN, USER_AUTH_ENABLED, username)
        return True

    # check number of total server connections
    try:
        conns = vpn.get_server_conns()
    except Exception:
        conns = 0

    if conns > MAX_CONNS_SERVER:
        print '{0}: plugin={1} username={2} server_conns={3}/{4}'.\
              format(stack()[0][3], DNS_SUB_DOMAIN, username,
                     conns, MAX_CONNS_SERVER)
        return False

    # check number of concurrent client connections
    try:
        conns = vpn.get_client_conns(user=uid)
    except Exception:
        conns = 0

    if conns > MAX_CONNS_CLIENT:
        print '{0}: plugin={1} username={2} client_conns={3}/{4}'.\
              format(stack()[0][3], DNS_SUB_DOMAIN, username,
                     conns, MAX_CONNS_CLIENT)
        return False

    result = False
    if plugin_loader.plugin and 'auth_user' in dir(plugin_loader.plugin):
        result = plugin_loader.plugin.auth_user(username, password)
        print '{0}: result={1} plugin={2} user_auth_enabled={3} username={4} password={5}'.\
              format(stack()[0][3], result, DNS_SUB_DOMAIN,
                     USER_AUTH_ENABLED, username, password)
    return result


if __name__ == '__main__':
    try:
        username = os.getenv('username')
        passwd = os.getenv('password')
        result = authenticate(username=username, password=passwd)
    except Exception as e:
        result = None

    if result: sys.exit(0)
    sys.exit(1)
