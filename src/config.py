# -*- coding: utf-8 -*-

import sys
import os
import uuid


AF = int(os.getenv('AF', 4))
AP = int(os.getenv('AP', 1))
UPNP = int(os.getenv('UPNP', 0))
AF_INETS = [int(af) for af in os.getenv('AF_INETS', '4 6').split()]

# 1=public server; 3=mixed; 4=private server
SERVER_DEVICE_TYPES = [
    int(sdt) for sdt in os.getenv('SERVER_DEVICE_TYPES', '1 3 4').split()
]

# 2=unblocking; 5=VPN; 6=Tor
CLIENT_DEVICE_TYPES = [
    int(cdt) for cdt in os.getenv('CLIENT_DEVICE_TYPES', '2 3 5').split()
]

# 0=buffered read; 1=cached read; 2=write
IOTESTS = [
    int(iot) for iot in os.getenv('IOTESTS', '0 1 2').split()
]

REQUESTS_VERIFY = bool(int(os.getenv('REQUESTS_VERIFY', 1)))
OPENVPN_BINARY = os.getenv('OPENVPN_BINARY', None)
OPENVPN_VERSION = os.getenv('OPENVPN_VERSION', None)
DEFAULT_TRIES = int(os.getenv('DEFAULT_TRIES', 3))
DEFAULT_DELAY = int(os.getenv('DEFAULT_DELAY', 2))
DEFAULT_BACKOFF = int(os.getenv('DEFAULT_BACKOFF', 2))
SKIP_DNS = int(os.getenv('SKIP_DNS', 0))
RESIN = int(os.getenv('RESIN', 0))
LOG_CLIENT_STATS = int(os.getenv('LOG_CLIENT_STATS', 1))
LOG_SERVER_STATS = int(os.getenv('LOG_SERVER_STATS', 1))
TUN_PROTO = tuple(os.getenv('TUN_PROTO', 'udp tcp').split(' '))
TUN_MGMT = int(os.getenv('TUN_MGMT', 0))
MGMT_IFACE = os.getenv('MGMT_IFACE', 'tun1')
TUN_IFACE_UDP = os.getenv('TUN_IFACE_UDP', 'tun2')
TUN_IFACE_TCP = os.getenv('TUN_IFACE_TCP', 'tun3')
TUN_IFACE = os.getenv('TUN_IFACE', 'tun4')
VPN_HOST = os.getenv('VPN_HOST', 'localhost')
VPN_UDP_MGMT_PORT = int(os.getenv('VPN_UDP_MGMT_PORT', 7505))
VPN_TCP_MGMT_PORT = int(os.getenv('VPN_TCP_MGMT_PORT', 7506))
SUPPRESS_TS = int(os.getenv('SUPPRESS_TS', 1))
API_VERSION = os.getenv('API_VERSION', '1.0')
API_SECRET = os.getenv('API_SECRET', None)
DNS_DOMAIN = os.getenv('DNS_DOMAIN', 'belodedenko.me')
DNS_SUB_DOMAIN = os.getenv('DNS_SUB_DOMAIN', 'blackbox')
WORKDIR = os.getenv('WORKDIR', '/mnt/%s' % DNS_SUB_DOMAIN)
TEMPDIR = os.getenv('TEMPDIR', '/dev/shm')
DATADIR = os.getenv('DATADIR', '/data')
DNS_SERVERS = os.getenv('DNS_SERVERS', '1.1.1.1 1.0.0.1').split()
DNS6_SERVERS = os.getenv('DNS6_SERVERS', '2606:4700:4700::1111 2606:4700:4700::1001').split()
MGMT_HOST = os.getenv('MGMT_HOST', 'http://mgmt.%s' % DNS_DOMAIN)
API_HOST = os.getenv('API_HOST', 'https://api-dev.%s' % DNS_DOMAIN)
DNS_HOST = os.getenv('DNS_HOST', '%s.%s' % (DNS_SUB_DOMAIN, DNS_DOMAIN))
POLL_FREQ = int(os.getenv('POLL_FREQ', 150)) # X times per cycle (e.g. LOOP_CYCLE / POLL_FREQ = 4)
LOOP_CYCLE = int(os.getenv('LOOP_CYCLE', 600)) # cycles
LOOP_TIMER = float(os.getenv('LOOP_TIMER', 0.1)) # seconds per cycle
DEVICE_TYPE = int(os.getenv('DEVICE_TYPE', 2))
GUID = os.getenv('RESIN_DEVICE_UUID', str(uuid.uuid4()))
PAIRED_DEVICE_GUID = os.getenv('PAIRED_DEVICE_GUID', None)
THRESHOLD = int(os.getenv('THRESHOLD', 99))
PING_TIMEOUT = int(os.getenv('PING_TIMEOUT', 5))
PING_COUNT = int(os.getenv('PING_COUNT', 10))
DEBUG = bool(int(os.getenv('DEBUG', 0)))
DEBUGGER = bool(int(os.getenv('DEBUGGER', 0)))
MAX_RATE = int(os.getenv('MAX_RATE', 5))
MAX_CONNS_SERVER = int(os.getenv('MAX_CONNS_SERVER', 100))
MAX_CONNS_CLIENT = int(os.getenv('MAX_CONNS_CLIENT', 2))
CONN_TIMEOUT = int(os.getenv('CONN_TIMEOUT', 5))
CLIENT_CONFIG = '%s/client.ovpn' % WORKDIR
TARGET_COUNTRY = os.getenv('TARGET_COUNTRY', 'United States')
GEOIP_OVERRIDE = os.getenv('GEOIP_OVERRIDE', None)
COUNTRY_OVERRIDE = os.getenv('COUNTRY_OVERRIDE', None)
CIPHER = os.getenv('CIPHER', 'none') # default: BF-CBC
AUTH = os.getenv('AUTH', 'none') # default: SHA1
USER_AUTH_ENABLED = int(os.getenv('USER_AUTH_ENABLED', 1))
PAYPAL_SUBSCRIPTION_CHECK = int(os.getenv('PAYPAL_SUBSCRIPTION_CHECK', 1))
BITCOIN_PAYMENT_CHECK = int(os.getenv('BITCOIN_PAYMENT_CHECK', 1))
POLICY_ROUTING_CHECK = int(os.getenv('POLICY_ROUTING_CHECK', 1))
STUNNEL = int(os.getenv('STUNNEL', 0))
PAIRED_DEVICES_FREE = int(os.getenv('PAIRED_DEVICES_FREE', 1))
WANPROXY = os.getenv('WANPROXY', None) # proxy transports: SOCAT or SSH
DOCKER_SSH_PORT = int(os.getenv('DOCKER_SSH_PORT', 2222))
TUN_MTU = os.getenv('TUN_MTU', '1500')
FRAGMENT = os.getenv('FRAGMENT', None)
VPN_USERNAME = os.getenv('VPN_USERNAME', None)
VPN_PROVIDER = os.getenv('VPN_PROVIDER', None)
VPN_LOCATION_GROUP = os.getenv('VPN_LOCATION_GROUP', None)
VPN_LOCATION = os.getenv('VPN_LOCATION', None)
VPN_PASSWD = os.getenv('VPN_PASSWD', None)
OPENVPN_PORT = os.getenv('OPENVPN_PORT', '1194')
WANPROXY_PORT= os.getenv('WANPROXY_PORT', '3300')
SOCAT_PORT= os.getenv('SOCAT_PORT', '3302')
EXPLICIT_EXIT_NOTIFY = int(os.getenv('EXPLICIT_EXIT_NOTIFY', 1))

ON_POSIX = '' in sys.builtin_module_names

os.environ['REQUESTS_CA_BUNDLE'] = os.getenv(
    'REQUESTS_CA_BUNDLE', '{}/cacert.pem'.format(DATADIR)
)
