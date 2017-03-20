#!/usr/bin/env python

import base64, hashlib, random

def generate_hash_key():
    """
    @return: A hashkey for use to authenticate agains the API.
    """
    return base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(),
                            random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')

print generate_hash_key()
