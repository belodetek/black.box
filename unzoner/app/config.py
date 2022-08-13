# -*- coding: utf-8 -*-

import os


LISTEN_ADDR = os.getenv('LISTEN_ADDR', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DNS_SUB_DOMAIN = os.getenv('DNS_SUB_DOMAIN', 'blackbox')
DEBUG = bool(int(os.getenv('DEBUG', 0)))
DEBUGGER = bool(int(os.getenv('DEBUGGER', 0)))
TEMPDIR = os.getenv('TEMPDIR', '/dev/shm')
