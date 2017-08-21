#!/usr/bin/env python
# -*- coding: utf-8 -*-
import imp
from config import DNS_SUB_DOMAIN

# dynamic import helper for Nuitka compiler
try:
    import plugin
except:
    try:
        plugin = imp.load_source(\
            'plugin', '{0}/{1}.plugin'.format('src', DNS_SUB_DOMAIN))
    except:
        pass
