#!/usr/bin/env python

import os
import sys

from common import log

if __name__ == '__main__':
    try:
        msg = sys.argv[1]
        log(msg)
    except IndexError:
        log('Hello world!')
