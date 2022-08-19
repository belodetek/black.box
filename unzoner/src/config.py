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

API_SECRET = os.getenv('API_SECRET', None)
API_VERSION = os.getenv('API_VERSION', '1.0')
AUTH = os.getenv('AUTH', 'none') # default: SHA1
BITCOIN_PAYMENT_CHECK = int(os.getenv('BITCOIN_PAYMENT_CHECK', 1))
CIPHER = os.getenv('CIPHER', 'none') # default: BF-CBC
CONN_TIMEOUT = int(os.getenv('CONN_TIMEOUT', 5))
COUNTRY_OVERRIDE = os.getenv('COUNTRY_OVERRIDE', None)
DATADIR = os.getenv('DATADIR', '/data')
DEBUG = bool(int(os.getenv('DEBUG', 0)))
DEBUGGER = bool(int(os.getenv('DEBUGGER', 0)))
DEFAULT_BACKOFF = int(os.getenv('DEFAULT_BACKOFF', 2))
DEFAULT_DELAY = int(os.getenv('DEFAULT_DELAY', 2))
DEFAULT_TRIES = int(os.getenv('DEFAULT_TRIES', 3))
DEVICE_TYPE = int(os.getenv('DEVICE_TYPE', 2))
DNS_DOMAIN = os.getenv('DNS_DOMAIN')

DNS_SUB_DOMAIN = os.getenv('DNS_SUB_DOMAIN', 'blackbox')
API_HOST = os.getenv('API_HOST', 'https://api-dev.{}'.format(DNS_DOMAIN))
DNS_HOST = os.getenv('DNS_HOST', '{}.{}'.format(DNS_SUB_DOMAIN, DNS_DOMAIN))
MGMT_HOST = os.getenv('MGMT_HOST', 'http://mgmt.{}'.format(DNS_DOMAIN))
WORKDIR = os.getenv('WORKDIR', '/mnt/{}'.format(DNS_SUB_DOMAIN))
CLIENT_CONFIG = '{}/client.ovpn'.format(WORKDIR)

DNS_SERVERS = os.getenv('DNS_SERVERS', '1.1.1.1 1.0.0.1').split()
DNS6_SERVERS = os.getenv('DNS6_SERVERS', '2606:4700:4700::1111 2606:4700:4700::1001').split()
DOCKER_SSH_PORT = int(os.getenv('DOCKER_SSH_PORT', 2222))
EXPLICIT_EXIT_NOTIFY = int(os.getenv('EXPLICIT_EXIT_NOTIFY', 1))
FRAGMENT = os.getenv('FRAGMENT', None)
GEOIP_OVERRIDE = os.getenv('GEOIP_OVERRIDE', None)
GUID = os.getenv('RESIN_DEVICE_UUID', str(uuid.uuid4()))
LOG_CLIENT_STATS = int(os.getenv('LOG_CLIENT_STATS', 1))
LOG_SERVER_STATS = int(os.getenv('LOG_SERVER_STATS', 1))
LOOP_CYCLE = int(os.getenv('LOOP_CYCLE', 300)) # cycles
LOOP_TIMER = float(os.getenv('LOOP_TIMER', 0.1)) # seconds per cycle
MAX_CONNS_CLIENT = int(os.getenv('MAX_CONNS_CLIENT', 2))
MAX_CONNS_SERVER = int(os.getenv('MAX_CONNS_SERVER', 100))
MAX_RATE = int(os.getenv('MAX_RATE', 5))
MGMT_IFACE = os.getenv('MGMT_IFACE', 'tun1')
OPENVPN_BINARY = os.getenv('OPENVPN_BINARY', None)
OPENVPN_PORT = os.getenv('OPENVPN_PORT', '1194')
OPENVPN_VERSION = os.getenv('OPENVPN_VERSION', None)
PAIRED_DEVICE_GUID = os.getenv('PAIRED_DEVICE_GUID', None)
PAIRED_DEVICES_FREE = int(os.getenv('PAIRED_DEVICES_FREE', 1))
PAYPAL_SUBSCRIPTION_CHECK = int(os.getenv('PAYPAL_SUBSCRIPTION_CHECK', 1))
PING_COUNT = int(os.getenv('PING_COUNT', 10))
PING_TIMEOUT = int(os.getenv('PING_TIMEOUT', 5))
POLICY_ROUTING_CHECK = int(os.getenv('POLICY_ROUTING_CHECK', 1))
POLL_FREQ = int(os.getenv('POLL_FREQ', 100)) # X times per cycle (e.g. LOOP_CYCLE / POLL_FREQ = 4)
REMOTE_OVERRIDE = os.getenv('REMOTE_OVERRIDE')
REQUESTS_VERIFY = bool(int(os.getenv('REQUESTS_VERIFY', 1)))
RESIN = int(os.getenv('RESIN', 0))
SKIP_DNS = int(os.getenv('SKIP_DNS', 0))
SOCAT_PORT= os.getenv('SOCAT_PORT', '3302')
STUNNEL = int(os.getenv('STUNNEL', 0))
SUPPRESS_TS = int(os.getenv('SUPPRESS_TS', 1))
TARGET_COUNTRY = os.getenv('TARGET_COUNTRY', 'United States')
TEMPDIR = os.getenv('TEMPDIR', '/dev/shm')
THRESHOLD = int(os.getenv('THRESHOLD', 99))
TUN_IFACE = os.getenv('TUN_IFACE', 'tun4')
TUN_IFACE_TCP = os.getenv('TUN_IFACE_TCP', 'tun3')
TUN_IFACE_UDP = os.getenv('TUN_IFACE_UDP', 'tun2')
TUN_MGMT = int(os.getenv('TUN_MGMT', 0))
TUN_MTU = os.getenv('TUN_MTU', '1500')
TUN_PROTO = tuple(os.getenv('TUN_PROTO', 'udp tcp').split(' '))
USER_AUTH_ENABLED = int(os.getenv('USER_AUTH_ENABLED', 1))
VPN_HOST = os.getenv('VPN_HOST', 'localhost')
VPN_LOCATION = os.getenv('VPN_LOCATION', None)
VPN_LOCATION_GROUP = os.getenv('VPN_LOCATION_GROUP', None)
VPN_PASSWD = os.getenv('VPN_PASSWD', None)
VPN_PROVIDER = os.getenv('VPN_PROVIDER', None)
VPN_TCP_MGMT_PORT = int(os.getenv('VPN_TCP_MGMT_PORT', 7506))
VPN_UDP_MGMT_PORT = int(os.getenv('VPN_UDP_MGMT_PORT', 7505))
VPN_USERNAME = os.getenv('VPN_USERNAME', None)
WANPROXY = os.getenv('WANPROXY', None) # proxy transports: SOCAT or SSH
WANPROXY_PORT= os.getenv('WANPROXY_PORT', '3300')

ON_POSIX = '' in sys.builtin_module_names

os.environ['REQUESTS_CA_BUNDLE'] = os.getenv(
    'REQUESTS_CA_BUNDLE', '{}/cacert.pem'.format(DATADIR)
)
