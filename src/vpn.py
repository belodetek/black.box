#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import re
import signal
import requests
import json

from time import sleep
from inspect import stack
from traceback import print_exc
from threading  import Thread
from subprocess import Popen, PIPE
from Queue import Queue

import auth
import plugin_loader

from paypal import get_jwt_payload
from common import retry, log
from api import *
from utils import *
from config import *


PROTOS = list(TUN_PROTO)
country = None
host = None
ipaddr = None
qtype = None
c_proto = None
c_wpid = None
s_wpid = None
s_wport = None


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def run_openvpn_mgmt_cmd(host=VPN_HOST, port=VPN_UDP_MGMT_PORT, cmd='status 2'):
    s = None
    data = str()
    header = None

    try:
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            if DEBUG: log(
                'getaddrinfo: res={} af={} socktype={} proto={} canonname={} sa={}'.format(
                    res,
                    af,
                    socktype,
                    proto,
                    canonname,
                    sa
                )
            )
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                log(
                    'socket: msg={} af={} socktype={} proto={} canonname={} sa={}'.format(
                        msg,
                        af,
                        socktype,
                        proto,
                        canonname,
                        sa
                    )
                )
                s = None
                continue
            try:
                s.connect(sa)
            except socket.error as msg:
                s.close()
                s = None
                continue
            break

        header = recv_with_timeout(s)
        if DEBUG: print(header)
        s.sendall(b'%s\n' % cmd)
        data = recv_with_timeout(s)
        if DEBUG: print(data)
        s.sendall(b'quit\n')
        s.close()
    except:
        pass
    return data.split('\r\n')


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_openvpn_version(default='2.3.10'):
    version = default
    try:
        version = run_shell_cmd(['/usr/bin/env', 'openvpn', '--version'])[1].split()[1]
    except:
        pass
    return version


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_openvpn_binary(default='/usr/sbin/openvpn'):
    binary = default
    try:
        binary = run_shell_cmd(['/usr/bin/which', 'openvpn'])[1].split()[0]
    except:
        pass
    return binary


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def connect_node(family=AF):
    global PROTOS
    global c_proto
    global c_wpid
    global s_wpid
    global s_wport
    global ipaddr
    global country
    global host
    global qtype

    try:
        log('os.kill: {}'.format(c_wpid))
        os.kill(int(c_wpid), signal.SIGKILL)
    except:
        pass

    c_wpid = None

    try:
        log(
            'kill_remote_pid: {}'.format(
                kill_remote_pid(
                    ipaddr=ipaddr,
                    family=family,
                    pid=s_wpid
                )
            )
        )
    except:
        pass
        
    s_wpid = None
    s_wport = None

    if len(PROTOS) <= 0: PROTOS = list(TUN_PROTO) # start again
    c_proto = PROTOS.pop()
    tun_proto = c_proto
    
    env = os.environ.copy()
    if DEBUG: print(env)

    qtype = 'A'
    if family == 6:
        if get_geo_location(family=6):
            qtype = 'AAAA'
        else:
            family = 4

    cmd = [OPENVPN_BINARY, '--config', CLIENT_CONFIG, '--dev', TUN_IFACE]
    port = OPENVPN_PORT

    ############
    # VPN mode #
    ############
    if DEVICE_TYPE == 5 or (\
        DEVICE_TYPE == 3\
        and VPN_PROVIDER\
        and VPN_LOCATION_GROUP\
        and VPN_LOCATION\
        and VPN_USERNAME\
        and VPN_PASSWD\
    ):
        log(
            '{}: mode={} provider={} group={} location={} username={} password={}'.format(
                stack()[0][3],
                DEVICE_TYPE,
                VPN_PROVIDER,
                VPN_LOCATION_GROUP,
                VPN_LOCATION,
                VPN_USERNAME,
                VPN_PASSWD
            )
        )
        assert VPN_PROVIDER and VPN_LOCATION_GROUP and VPN_LOCATION \
               and VPN_USERNAME and VPN_PASSWD
   
    else:
        #########################
        # pairing mode override #
        #########################
        if PAIRED_DEVICE_GUID:
            try:
                ipaddr = get_node_by_guid(family=family)
                log(
                    'get_node_by_guid: ipaddr={} af={} guid={}'.format(
                        ipaddr,
                        family,
                        PAIRED_DEVICE_GUID
                    )
                )
                assert ipaddr
            except AssertionError as e:
                if DEBUG: print_exc()
                try:
                    assert family == 6 # fall-back to IPv4 if not already
                    ipaddr = get_node_by_guid(family=4)
                    log(
                        'get_node_by_guid: ipaddr={} af={} guid={}'.format(
                            ipaddr,
                            4,
                            PAIRED_DEVICE_GUID
                        )
                    )
                    assert ipaddr
                except AssertionError as e:
                    if DEBUG: print_exc()
                    log(
                        'get_node_by_guid: e={} af={}'.format(
                            repr(e),
                            family
                        )
                    )

        ###################
        # unblocking mode #
        ###################
        else:
            if family == 6 and not SKIP_DNS:
                try:
                    # try DNS resolution (IPv6)
                    country = get_alpha(TARGET_COUNTRY).lower()
                    host = '{}.{}'.format(country, DNS_HOST)
                    ipaddr = resolve_dns(host=host, record=qtype, family=family)    
                    assert ipaddr
                except Exception as e:
                    log(
                        'resolve_dns: e={} qtype={} family={}'.format(
                            repr(e),
                            qtype,
                            family
                        )
                    )
                    family = 4
                    qtype = 'A'
                    if DEBUG: print_exc()

            if family == 4 and not SKIP_DNS:
                try:
                    # try DNS resolution (IPv4)
                    country = get_alpha(TARGET_COUNTRY).lower()
                    host = '{}.{}'.format(country, DNS_HOST)
                    ipaddr = resolve_dns(host=host, record=qtype, family=family)
                    assert ipaddr
                except Exception as e:
                    log(
                        'resolve_dns: e={} qtype={} family={}'.format(
                            repr(e),
                            qtype,
                            family
                        )
                    )
                    if DEBUG: print_exc()

            log(
                '{}: qtype={} country={} host={} ipaddr={}'.format(
                    stack()[0][3],
                    qtype,
                    country,
                    host,
                    ipaddr
                )
            )
  
            if not ipaddr:
                if family == 6:
                    try:
                        # fall-back to API (IPv6)
                        ipaddr = get_node_by_country(family=family)
                        log(
                            'get_node_by_country: ipaddr={} af={}'.format(
                                stack()[0][3],
                                ipaddr,
                                family
                            )
                        )
                    except AssertionError as e:
                        log(
                            'get_node_by_country: e={} af={}'.format(
                                repr(e),
                                family
                            )
                        )
                        if DEBUG: print_exc()
                        family = 4
                        qtype = 'A'

                if family == 4:
                    try:
                        # fall-back to API (IPv4)
                        ipaddr = get_node_by_country(family=family)
                        log(
                            'get_node_by_country: ipaddr={} af={}'.format(
                                ipaddr,
                                family
                            )
                        )
                    except AssertionError as e:
                        log(
                            'get_node_by_country: e={} af={}'.format(
                                repr(e),
                                family
                            )
                        )
                        if DEBUG: print_exc()
            
        assert ipaddr

        if family == 6: tun_proto = '{}{}'.format(c_proto, family)
        log(
            '{}: mode={} remote={} port={} proto={} protos={} cipher={} auth={}'.format(
                stack()[0][3],
                DEVICE_TYPE,
                ipaddr,
                port,
                tun_proto,
                TUN_PROTO,
                CIPHER,
                AUTH
            )
        )

        ####################
        # stunnel override #
        ####################
        if STUNNEL:
            result = conf_stunnel_client(ipaddr)
            if DEBUG: print(result)

            result = restart_stunnel_client()
            if DEBUG: print(result)

            if result[0] == 0:
                ipaddr = 'localhost'
                tun_proto = 'tcp'
                if family == 6: tun_proto = '{}{}'.format(tun_proto, family)
                log(
                    '{}: stunnel={} proto={} ipaddr={}'.format(
                        stack()[0][3],
                        STUNNEL,
                        tun_proto,
                        ipaddr
                    )
                )

        #####################
        # WANProxy override #
        #####################
        if WANPROXY:
            (c_wpid, s_wpid, s_wport) = start_wanproxy_server(
                ipaddr=ipaddr,
                family=family,
                local_pid=c_wpid,
                remote_pid=s_wpid,
                port=s_wport
            )

            log(
                'start_wanproxy_server: ipaddr={} af={} local_pid={} remote_pid={} remote_port={} transport={}'.format(
                    ipaddr,
                    family,
                    c_wpid,
                    s_wpid,
                    s_wport,
                    WANPROXY
                )
            )

            port = WANPROXY_PORT
            ipaddr = 'localhost'
            tun_proto = 'tcp'
            if family == 6: tun_proto = '{}{}'.format(tun_proto, family)
            log(
                '{}: wan_proxy={} proto={} ipaddr={} port={}'.format(
                    stack()[0][3],
                    WANPROXY,
                    tun_proto,
                    ipaddr,
                    port
                )
            )

        if FRAGMENT and tun_proto == 'udp':
            cmd.append('--tun-mtu')
            cmd.append(TUN_MTU) 
            cmd.append('--mssfix')
            cmd.append('--fragment')
            cmd.append(FRAGMENT)

        if EXPLICIT_EXIT_NOTIFY in [1, 2] and tun_proto == 'udp':
            cmd.append('--explicit-exit-notify')
            cmd.append(str(EXPLICIT_EXIT_NOTIFY))

        cmd.append('--remote')
        cmd.append(ipaddr)
        cmd.append(port)
        cmd.append(tun_proto)
        cmd.append('--cipher')
        cmd.append(CIPHER)
        cmd.append('--auth')
        cmd.append(AUTH)

    log(
        '{}: ipaddr={} af={} qtype={} proto={} port={} country={} guid={} provider={} group={} location={} username={}'.format(
            stack()[0][3],
            ipaddr,
            family,
            qtype,
            tun_proto,
            port,
            TARGET_COUNTRY,
            PAIRED_DEVICE_GUID,
            VPN_PROVIDER,
            VPN_LOCATION_GROUP,
            VPN_LOCATION,
            VPN_USERNAME
        )
    )

    p = run_shell_cmd_nowait(cmd)
    stdoutq = Queue()
    stderrq = Queue()
    stdoutt = Thread(target=enqueue_output, args=(p.stdout, stdoutq))
    stderrt = Thread(target=enqueue_output, args=(p.stderr, stderrq))
    stdoutt.daemon = True
    stdoutt.start()
    stderrt.daemon = True
    stderrt.start()
    return stdoutq, stderrq, p, c_proto


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def start_server(proto='udp'):
    iface = TUN_IFACE_UDP
    if proto == 'tcp': iface = TUN_IFACE_TCP
    
    config = '{}/openvpn/{}_server.conf'.format(WORKDIR, proto)
    
    cmd = [
        OPENVPN_BINARY,
        '--config', config,
        '--dev', iface,
        '--proto', '{}6'.format(proto), '--port', OPENVPN_PORT,
        '--cipher', CIPHER,
        '--auth', AUTH
    ]

    if FRAGMENT and proto == 'udp':
        cmd.append('--tun-mtu')
        cmd.append(TUN_MTU) 
        cmd.append('--mssfix')
        cmd.append('--fragment')
        cmd.append(FRAGMENT)

    if EXPLICIT_EXIT_NOTIFY in [1, 2]\
       and proto == 'udp'\
       and bool(re.search('^2.4.', OPENVPN_VERSION)):
        cmd.append('--explicit-exit-notify')
        cmd.append(str(EXPLICIT_EXIT_NOTIFY)) 

    p = run_shell_cmd_nowait(cmd)
    stdoutq = Queue()
    stderrq = Queue()
    stdoutt = Thread(target=enqueue_output, args=(p.stdout, stdoutq))
    stderrt = Thread(target=enqueue_output, args=(p.stderr, stderrq))
    stdoutt.daemon = True
    stdoutt.start()
    stderrt.daemon = True
    stderrt.start()
    return stdoutq, stderrq, p


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def _get_client_conns(user=GUID, proto='udp'):
    conns = 0
    stats = open(
        '{}/openvpn.{}.status'.format(
            DATADIR,
            proto
        )
    ).read().split('\n')
    for lines in stats:
        line = lines.split(',')        
        if 'CLIENT_LIST' in line and line[0] in ['CLIENT_LIST'] and line[-1] and line[1] == user:
            conns = conns + 1
    return conns


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_client_conns(user=GUID):
    try:
        udp_conns = _get_client_conns(user=user) # udp stats
    except:
        udp_conns = 0
    try:
        tcp_conns = _get_client_conns(user=user, proto='tcp') # tcp stats
    except:
        tcp_conns = 0
    return udp_conns + tcp_conns


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_server_conns_by(proto='udp'):
    conns = 0
    stats = open(
        '{}/openvpn.{}.status'.format(
            DATADIR,
            proto
        )
    ).read().split('\n')
    for lines in stats:
        line = lines.split(',')        
        if 'CLIENT_LIST' in line and line[0] in ['CLIENT_LIST'] and line[-1]: conns = conns + 1
    return conns


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_server_conns(status=[True, True]):
    conns = 0
    stats = [None, None]
    try:
        if status[0]: stats[0] = get_server_conns_by() # udp stats        
        if status[1]: stats[1] = get_server_conns_by(proto='tcp') # tcp stats
    except:
        pass
    if stats[0]: conns = int(stats[0]) # udp vpn connection count
    if stats[1]: conns = conns + int(stats[1]) # udp + tcp vpn connection count
    return conns


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_load_stats(host=VPN_HOST, port=VPN_UDP_MGMT_PORT):
    stats = (0, 0, 0)
    try:
        load_stats = run_openvpn_mgmt_cmd(host=host, port=port, cmd='load-stats')
        p = re.compile('^SUCCESS: nclients=([\d]+),bytesin=([\d]+),bytesout=([\d]+)$')
        m = p.search(load_stats[0])
        try:
            stats = m.groups()
        except:
            pass
    except:
        pass
    return stats


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_status(user=GUID, proto='udp'):
    status = list()
    status = open(
        '{}/openvpn.{}.status'.format(
            DATADIR,
            proto
        )
    ).read().split('\n')
    return status


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def _get_status(host=VPN_HOST, port=VPN_UDP_MGMT_PORT):
    status = list()
    status = run_openvpn_mgmt_cmd(host=host, port=port)
    return status


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_client_status():
    bytesin = 0
    bytesout = 0
    try:
        status = open(
            '{}/client.status'.format(
                TEMPDIR
            )
        ).read().split('\n')
        bytesin = [line.split(',')[1] for line in status if line.split(',')[0] == 'TCP/UDP read bytes'][0]
        bytesout = [line.split(',')[1] for line in status if line.split(',')[0] == 'TCP/UDP write bytes'][0]
    except IndexError:
        pass
    return (bytesin, bytesout)


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_clients():
    clients = list()
    udp_clients = list()
    try:
        udp_clients = get_status()
    except:
        pass
    for lines in udp_clients:
        line = lines.split(',')
        if 'CLIENT_LIST' in line and line[0] in ['CLIENT_LIST'] and line[-1]:
            clients.append(line[1])
    tcp_clients = list()
    try:
        tcp_clients = get_status(proto='tcp')
    except:
        pass
    for lines in tcp_clients:
        line = lines.split(',')
        if 'CLIENT_LIST' in line and line[0] in ['CLIENT_LIST'] and line[-1]:
            clients.append(line[1])
    return clients


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def reauthenticate_clients():
    count = 0
    while True:
        clients = get_clients()
        killed = list()
        print(
            '{}: count={} clients={}'.format(
                stack()[0][3],
                count,
                len(clients)
            )
        )
        for client in clients:
            # password check (resin.io Data API)
            jwtoken = None
            try:
                password = get_device_env_by_name(guid=client, name='TUN_PASSWD')[:16]
                assert password
            except Exception as e:
                # authenticate against JWT recorded against PayPal billing agreement
                try:
                    jwtoken = decode_jwt_payload(encoded=get_jwt_payload_from_paypal(baid=client))
                    password = jwtoken['p'][:16]
                    assert password
                except:
                    password = None

            if not password: break

            result = auth.authenticate(username=client, password=password)
            print(
                'get_device_env_by_name: client={} password={}'.format(
                    client,
                    password
                )
            )
            if not result and client != 'UNDEF':
                for port in [VPN_UDP_MGMT_PORT, VPN_TCP_MGMT_PORT]:    
                    try:
                        print(
                            'run_openvpn_mgmt_cmd: port={} cmd=kill client={} result={}'.format(
                                port,
                                client,
                                result
                            )
                        )
                        print(
                            run_openvpn_mgmt_cmd(
                                port=port,
                                cmd='kill {}'.format(
                                    client
                                )
                            )
                        )
                        killed.append(client)
                    except:
                        pass
        print(
            '{}: count={} killed={}'.format(
                stack()[0][3],
                count,
                len(killed)
            )
        )
        sleep(3600)
        count = count + 1


def log_client_stats(status=False, country=TARGET_COUNTRY):
    if LOG_CLIENT_STATS:
        for family in AF_INETS:
            data = get_geo_location(family=family)
            if not data: break

            # 1 = up
            # 0 = down
            data['status'] = sum([int(el) for el in [status]])
            
            data['bytesin'] = 0
            data['bytesout'] = 0
            data['conns'] = 0
            data['hostapd'] = AP
            data['weight'] = MAX_CONNS_CLIENT

            if DEVICE_TYPE == 5:
                data['country'] = country
                
            if COUNTRY_OVERRIDE:
                log('{}: country={}'.format(stack()[0][3], COUNTRY_OVERRIDE))
                data['country'] = COUNTRY_OVERRIDE

            if GEOIP_OVERRIDE:
                log('{}: ip={}'.format(stack()[0][3], GEOIP_OVERRIDE))
                data['ip'] = GEOIP_OVERRIDE

            if DEVICE_TYPE in CLIENT_DEVICE_TYPES:
                try:
                    data['conns'] = get_stations() # wireless client count
                    data['bytesin'] = get_client_status()[0]
                    data['bytesout'] = get_client_status()[1]
                except:
                    pass

            log('{}: af={} data={}'.format(stack()[0][3], family, data))
            print(put_device(family=family, data=data))

    # client logging plug-in(s)
    log('{}: plugin={}'.format(stack()[0][3], DNS_SUB_DOMAIN))
    if plugin_loader.plugin and \
       'log_plugin_client' in dir(plugin_loader.plugin):
        result = plugin_loader.plugin.log_plugin_client(status=status)
       

def log_server_stats(status=[False, False]):
    if LOG_SERVER_STATS:
        for family in AF_INETS:
            data = get_geo_location(family=family)
            if not data: break

            # 2 = udp+tcp; 1 = udp or tcp; 0 = down
            data['status'] = sum([int(el) for el in status])
            data['conns'] = 0        
            data['bytesin'] = 0
            data['bytesout'] = 0
            data['cipher'] = CIPHER
            data['auth'] = AUTH
            data['upnp'] = UPNP
            data['weight'] = MAX_CONNS_SERVER
            
            if COUNTRY_OVERRIDE:
                log('{}: country={}'.format(stack()[0][3], COUNTRY_OVERRIDE))
                data['country'] = COUNTRY_OVERRIDE

            if GEOIP_OVERRIDE:
                log('{}: ip={}'.format(stack()[0][3], GEOIP_OVERRIDE))
                data['ip'] = GEOIP_OVERRIDE

            if DEVICE_TYPE in SERVER_DEVICE_TYPES:
                stats = [None, None]
                if status[0]: stats[0] = int(get_server_conns_by()) # udp stats
                if status[1]: stats[1] = int(get_server_conns_by(proto='tcp')) # tcp stats
                
                if stats[0]:
                    data['conns'] = int(stats[0]) # udp vpn connection count

                    try:
                        data['bytesin'] = int(get_load_stats()[1])
                    except:
                        pass
                    
                    try:
                        data['bytesout'] = int(get_load_stats()[2])
                    except:
                        pass
                    
                if stats[1]:
                    data['conns'] = data['conns'] + int(stats[1]) # udp + tcp vpn connection count

                    try:
                        data['bytesin'] = data['bytesin'] + int(get_load_stats(port=VPN_TCP_MGMT_PORT)[1])
                    except:
                        pass

                    try:
                        data['bytesout'] = data['bytesout'] + int(get_load_stats(port=VPN_TCP_MGMT_PORT)[2])
                    except:
                        pass

            log('{}: af={} data={}'.format(stack()[0][3], family, data))
            print(put_device(family=family, data=data))

    # additional server logging plug-in(s)
    log('{}: plugin={}'.format(stack()[0][3], DNS_SUB_DOMAIN))
    if plugin_loader.plugin and 'log_plugin_server' in dir(plugin_loader.plugin):
        result = plugin_loader.plugin.log_plugin_server(status=status)


def conf_stunnel_client(node=None, conf='/etc/stunnel/stunnel-client.conf',
                        template='/etc/stunnel/stunnel-client.template.conf'):
    
    if not node: return None
    f = open(template, 'r')
    template = f.read()
    f.close()
    template = template.replace('{{OPENVPN_SERVER}}', node)
    f = open(conf, 'w')
    f.write(template)
    f.close()
    
    return template


def restart_stunnel_client(
    stunnel_bin='/usr/bin/stunnel',
    conf='/etc/stunnel/stunnel-client.conf'
):
    print(
        run_shell_cmd(
            [
                '/usr/bin/pkill',
                '-f',
                '%s %s' % (stunnel_bin, conf)
            ]
        )
    )
    return run_shell_cmd(['%s' % stunnel_bin, '%s' % conf])


def start_wanproxy_server(ipaddr=None, family=4, local_pid=None,
                          remote_pid=None, port=None, ssh_port=DOCKER_SSH_PORT):

    if WANPROXY == 'SSH':
        remote_guid = get_guid_by_public_ipaddr(ipaddr=ipaddr, family=family)
        assert remote_guid
        if DEBUG: print(
            'get_guid_by_public_ipaddr: ipaddr={} family={} remote_guid={}'.format(
                ipaddr,
                family,
                remote_guid
            )
        )

    if not (port and remote_pid):
        if WANPROXY == 'SSH':
            # start WANProxy server instance and get remote port for forwarding
            result = run_shell_cmd(
                [
                    'ssh', '-i', '%s/id_rsa' % WORKDIR,
                    '-o StrictHostKeyChecking=no',
                    'root@%s' % ipaddr,
                    '-p', '%s' % str(ssh_port),
                    'bash',
                    '-c',
                    '"source %s/functions; source %s/.env; start_wanproxy_server"' % (
                        WORKDIR,
                        TEMPDIR
                    )
                ]
            )
            if DEBUG: print(result)
            remote_pid = result[1].split()[0]
            port = result[1].split()[1]

    if not local_pid:
        if WANPROXY == 'SSH':
            # start SSH tunnel
            result = run_background_shell_cmd(
                [
                    'ssh', '-i', '%s/id_rsa' % WORKDIR,
                    '-fN','-o StrictHostKeyChecking=no',
                    '-L 3301:localhost:%s' % str(port),
                    '-p', '%s' % str(ssh_port),
                    'root@%s' % ipaddr
                ]
            )
            if DEBUG: print(result.__dict__)
            local_pid = str(int(result.pid) + 1)
            
        if WANPROXY == 'SOCAT':
            # start SOCAT local listener
            result = run_shell_cmd_nowait(
                [
                    '/usr/bin/socat',
                    'TCP%s-LISTEN:3301,bind=localhost,su=nobody,fork,reuseaddr' % str(
                        family
                    ),
                    'TCP%s:%s:%s' % (str(family), ipaddr, SOCAT_PORT)
                ]
            )
            if DEBUG: print(result.__dict__)
            local_pid = str(result.pid)
            
    return (local_pid, remote_pid, port)


def kill_remote_pid(ipaddr=None, family=4, pid=None, ssh_port=DOCKER_SSH_PORT):    
    if WANPROXY == 'SSH':
        remote_guid = get_guid_by_public_ipaddr(ipaddr=ipaddr, family=family)
        assert remote_guid
        if DEBUG: print(
            'get_guid_by_public_ipaddr: ipaddr={} family={} remote_guid={}'.format(
                ipaddr,
                family,
                remote_guid
            )
        )

    result = None
    if pid and WANPROXY == 'SSH':
        # kill remote pid
        result = run_shell_cmd(
            [
                'ssh', '-i', '%s/id_rsa' % WORKDIR,
                '-o StrictHostKeyChecking=no',
                'root@%s' % ipaddr,
                '-p', '%s' % str(ssh_port),
                'bash', '-c', '"kill -9 %s"' % str(pid)
            ]
        )
        if DEBUG: print(result)
    return result


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def disconnect_clients():
    disconnected = list()
    while True:
        if os.path.exists('{}/disconnect_clients'.format(DATADIR)):
            if not 'client_disconnect' in dir(plugin_loader.plugin): break
            clients = get_clients()
            print('{}: clients={}'.format(stack()[0][3], len(clients)))
            for client in clients:
                if client not in ['UNDEF']:
                    try:
                        result = plugin_loader.plugin.client_disconnect(client)
                        disconnected.append(client)
                        print(
                            'client_disconnect: client={} result={}'.format(
                                client,
                                result
                            )
                        )
                    except:
                        pass

            if os.path.exists('{}/disconnect_clients'.format(DATADIR)):
                os.remove('{}/disconnect_clients'.format(DATADIR))

            print(
                '{}: plugin={} disconnected={}'.format(
                    stack()[0][3],
                    DNS_SUB_DOMAIN,
                    len(disconnected)
                )
            )
        sleep(1)
    sleep(3600)


if not OPENVPN_VERSION: OPENVPN_VERSION = get_openvpn_version()
if not OPENVPN_BINARY: OPENVPN_BINARY = get_openvpn_binary()
