#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from uuid import uuid4
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect

from config import *


KEY = '/mnt/{}/openvpn/server.key'.format(DNS_SUB_DOMAIN)
CERT = '/mnt/{}/openvpn/server.crt'.format(DNS_SUB_DOMAIN)

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid4().hex
app.debug=DEBUGGER
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
namespace = '/{}'.format(DNS_SUB_DOMAIN)
thread = None


def background_thread():
    from common import read_pipe, open_pipe

    PIPE = '{}/{}'.format(TEMPDIR, DNS_SUB_DOMAIN)
    if not os.path.exists(PIPE): os.mkfifo(PIPE)

    FIFO = None
    count = 2
    while True:
        socketio.sleep(1)
        if not FIFO: FIFO = open_pipe(pipe=PIPE)
        data = read_pipe(fifo=FIFO)
        if data:
            if DEBUG: print('read_pipe: {}'.format(repr(data)))
            for msg in data.decode('utf-8').split('\n'):
                if msg:
                    count += 1
                    socketio.emit(
                        'my_response',
                        {
                            'data': msg,
                            'count': count
                        },
                        namespace=namespace
                    )


@app.route('/')
def index():
    return render_template(
        'index.html',
        async_mode=socketio.async_mode,
        namespace=namespace
    )


@socketio.on('my_event', namespace=namespace)
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': message['data'],
            'count': session['receive_count']
        }
    )


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': 'client disconnected, reload to reconnect',
            'count': session['receive_count']
        }
    )
    disconnect()


@socketio.on('my_ping', namespace=namespace)
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace=namespace)
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': 'client connected',
            'count': session['receive_count']
        }
    )


@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
    session['receive_count'] = 0
    print('client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(
        app,
        debug=DEBUG,
        host=LISTEN_ADDR,
        port=PORT,
        keyfile=KEY,
        certfile=CERT
    )
