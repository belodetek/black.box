#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import errno

from time import sleep
from functools import wraps
from traceback import print_exc
from inspect import stack

from config import *
from hashlib import md5


PIPE = '{}/{}'.format(TEMPDIR, DNS_SUB_DOMAIN)
if not os.path.exists(PIPE): os.mkfifo(PIPE)


def retry(ExceptionToCheck, tries=DEFAULT_TRIES, delay=DEFAULT_DELAY, backoff=DEFAULT_BACKOFF, cdata=None):
    '''Retry calling the decorated function using an exponential backoff.
    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    '''
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries >= 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    print(
                        '{}, retrying in {} seconds (mtries={}): {}'.format(
                            repr(e),
                            mdelay,
                            mtries,
                            str(cdata)
                        )
                    )
                    if DEBUG == 1: print_exc()
                    sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


def get_md5(s):
    s = unicode(s)
    s = s.encode('utf-8')
    try:
        return md5(s).hexdigest()
    except:
        return s


def open_pipe(pipe=None):
    try:
        fifo = None
        try:
            fifo = os.open(pipe, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as e:
            if e.errno == errno.ENXIO: pass
            else: pass
        return fifo
    except:
        pass


def write_pipe(fifo=None, data=None):
    try:
        os.write(fifo, data)
    except OSError as e:
        if e.errno == errno.EPIPE: pass
        else: pass


def log(data):
    global FIFO
    try:
        if not FIFO: FIFO = open_pipe(pipe=PIPE)
        write_pipe(fifo=FIFO, data=data.encode())
    except:
        try:
            print(data.decode())
        except:
            print(data)


FIFO = open_pipe(pipe=PIPE)
