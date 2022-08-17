#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, errno
from traceback import print_exc
from inspect import stack

from config import *


def open_pipe(pipe=None):
    try:
        fifo = None
        try:
            fifo = os.open(pipe, os.O_RDONLY | os.O_NONBLOCK, 0)
        except OSError as e:
            if DEBUG: print_exc()

        if DEBUG: print('{}: pipe={} fifo={}'.format(
            stack()[0][3],
            repr(pipe),
            repr(fifo)
        ))
        return fifo

    except Exception as e:
        if DEBUG: print_exc()


def read_pipe(fifo=None):
    try:
        BUFFER_SIZE = 8192
        buffer = None
        try:
            buffer = os.read(fifo, BUFFER_SIZE)
        except OSError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                buffer = None
            else:
                if DEBUG: print_exc()

        if DEBUG: print('{}: buffer={}'.format(
            stack()[0][3],
            repr(buffer)
        ))

        return buffer

    except Exception as e:
        if DEBUG: print_exc()
