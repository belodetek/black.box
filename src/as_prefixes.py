#!/usr/bin/env python

import pyasn, os, sys
from traceback import print_exc

from ipaddr import (
    IPNetwork,
    IPv4Network,
    IPv6Network,
    collapse_address_list
)


DEBUG = bool(int(os.getenv('DEBUG', False)))
IPASN_DB = os.getenv('IPASN_DB', 'ipasn_20170201.1600.dat.gz')
DATADIR = os.getenv('DATADIR', '/data')


if __name__ == '__main__':
    af = 4
    try:
        af = int(sys.argv[1])
    except Exception:
        pass

    try:
        assert af in [4, 6]
        db = pyasn.pyasn('%s/%s' % (DATADIR, IPASN_DB))
        assert db
        asns = os.getenv('AS_NUMS')
        asns = asns.split()
        assert asns

    except Exception:
        if DEBUG: print_exc()
        sys.exit(1)

    asns = [asn.replace('AS', '') for asn in asns]

    nets = list()
    collapsed = None
    for asn in asns:
        try:
            result = db.get_as_prefixes(asn)
            if result:
                for net in result:
                    if IPNetwork(net).version == 4 and IPNetwork(net).version == af:
                        nets.append(IPv4Network(net))
                    if IPNetwork(net).version == 6 and IPNetwork(net).version == af:
                        nets.append(IPv6Network(net))

            collapsed = [str(net) for net in collapse_address_list(nets)]

        except Exception:
            if DEBUG: print_exc()
            pass

    if collapsed: print('\n'.join(collapsed))
