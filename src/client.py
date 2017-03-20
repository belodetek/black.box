#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, importlib
from inspect import stack

import nuitka
from common import retry
from config import (DEBUG, DNS_SUB_DOMAIN)


if __name__ == '__main__':
    try:
        op = sys.argv[1]
    except IndexError:
        pass
        sys.exit(0)

    uname = os.getenv('username')
    plugin = None
    result = False

    try:
        plugin = __import__('plugin')
        
    except ImportError:
        pass
        sys.exit(0)

    # connect plug-ins
    if op == 'connect':
        if plugin and 'client_connect' in dir(plugin):
            result = plugin.client_connect(uname)
            if result:
                print 'plugin=%s name=%s connected' % (DNS_SUB_DOMAIN, uname)
                
    # disconnect plug-ins
    if op == 'disconnect': 
        if plugin and 'client_disconnect' in dir(plugin):
            result = plugin.client_disconnect(uname)
            if result:
                print 'plugin=%s name=%s disconnected' % (DNS_SUB_DOMAIN, uname)

    sys.exit(0)
