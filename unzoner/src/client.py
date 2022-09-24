#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, importlib
from inspect import stack

from config import DNS_SUB_DOMAIN
from common import retry
import plugin


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def connect_disconnect(cmd=None, username=None):
    if not cmd in ['connect', 'disconnect']: return False
    if cmd == 'connect':
        if 'client_connect' in dir(plugin):
            result = plugin.client_connect(username=username)
            if result: print('plugin={} name={} connected'.format(
                DNS_SUB_DOMAIN,
                username
            ))

    if cmd == 'disconnect':
        if 'client_disconnect' in dir(plugin):
            result = plugin.client_disconnect(username=username)
            if result: print('plugin={} name={} disconnected'.format(
                DNS_SUB_DOMAIN,
                username
            ))

    return True


if __name__ == '__main__':
    try:
        op = sys.argv[1]
    except IndexError:
        pass

    uname = os.getenv('username')
    if op: connect_disconnect(cmd=op, username=uname)
    sys.exit(0)
