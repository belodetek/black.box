#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from traceback import print_exc

from config import DNS_SUB_DOMAIN, DEBUG

try:
    import plugin
except ImportError as e:
    print repr(e)
    if DEBUG: print_exc()
    try:
        from imp import load_source
        source = '{0}/{1}.plugin'.\
                 format(
                     os.path.dirname(
                         os.path.realpath(__file__)), DNS_SUB_DOMAIN)
        if DEBUG: print 'loading {0} from {1}'.\
           format(DNS_SUB_DOMAIN, source)
        plugin = load_source('plugin', source)
    except ImportError as e:
        print repr(e)
        if DEBUG: print_exc()
        plugin = None
