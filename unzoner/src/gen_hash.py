#!/usr/bin/env python

try:
    from secrets import token_urlsafe
except:
    from base64 import b64encode
    from hashlib import sha256
    from random import choice, getrandbits


def generate_hash_key():
    try:
        return token_urlsafe(32)
    except:
        return b64encode(
            sha256(str(getrandbits(256))).digest(),
            choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])
        ).rstrip('==')


print(generate_hash_key())
