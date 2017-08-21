#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, socket, fcntl, struct, re, json, jwt, dns.resolver
from time import time, sleep
from ping import quiet_ping
from inspect import stack
from subprocess import Popen, PIPE
from threading import Thread
from Queue import Queue, Empty
from common import retry
from traceback import print_exc

from config import (WORKDIR, DEBUG, TEMPDIR, CONN_TIMEOUT, MGMT_HOST,
                    DNS_SERVERS, DNS_HOST, THRESHOLD, PING_COUNT, PING_TIMEOUT,
                    TUN_IFACE, AF, TARGET_COUNTRY, DEVICE_TYPE, LOOP_TIMER,
                    LOOP_CYCLE, ON_POSIX, DNS6_SERVERS, GUID)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def recv_with_timeout(s, timeout=5):
    data = list()
    
    try:
        # make socket non blocking
        s.setblocking(False)
         
        buffer = ''
         
        # set begin time
        begin = time()
        
        while True:
            # if you got some data, then break after timeout
            if data and time() - begin > timeout:
                break
             
            # if you got no data at all, wait a little longer, twice the timeout
            elif time() - begin > timeout * 2:
                break
             
            # receive some data
            try:
                buffer = s.recv(1024)
                if buffer:
                    data.append(buffer)
                    # reset the begin time for measurement
                    begin = time()
                else:
                    sleep(LOOP_TIMER)
            except:
                pass

    except Exception as e:
        print repr(e)
        if DEBUG: print_exc()
        pass
     
    return ''.join(data)


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
        
    out.close()
    
    
@retry(Exception, cdata='method=%s()' % stack()[0][3])
def run_shell_cmd(cmd):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    output, err = p.communicate()
    return p.returncode, output, err, p.pid


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def run_background_shell_cmd(cmd):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    stat = p.poll()
    while stat == None:
        stat = p.poll()
    return p


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def run_shell_cmd_nowait(cmd):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    return p


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_hostname():
    hostname = 'localhost'
    try:
        hostname = socket.gethostname()
    except Exception:
        pass

    return hostname


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_geo_location(family=AF):
    data = dict()
    cmd = ['curl', '-%d' % family,
           '--connect-timeout', '%d' % CONN_TIMEOUT,
           '--max-time', '%d' % CONN_TIMEOUT * 2,
           '%s/json' % MGMT_HOST]

    # get the VPN server location, not the location of the device
    if DEVICE_TYPE == 5 and get_ip_address(TUN_IFACE):
        cmd.append('--interface')
        cmd.append(TUN_IFACE)

    try:
        result = run_shell_cmd(['curl', '-%d' % family,
                                '--connect-timeout', '%d' % CONN_TIMEOUT,
                                '--max-time', '%d' % CONN_TIMEOUT * 2,
                                '%s/json' % MGMT_HOST])

        if DEBUG: print 'run_shell_cmd: %r' % (result,)

        assert result[0] == 0
        data = json.loads(result[1])     
    except Exception as e:
        print '%s: family=%s data=%s e=%r' % (stack()[0][3], family,
                                              data, repr(e))
        if DEBUG: print_exc()
        pass

    return data


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915,  # SIOCGIFADDR
                                            struct.pack('256s', ifname[:15]))[20:24])
    except IOError:
        pass


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_default_iface():
    route = "/proc/net/route"
    with open(route) as f:
        for line in f.readlines():
            try:
                iface, dest, _, flags, _, _, _, _, _, _, _, =  line.strip().split()
                if dest != '00000000' or not int(flags, 16) & 2:
                    continue
                return iface
            except:
                continue


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def ping_host(host='localhost', timeout=PING_TIMEOUT, count=PING_COUNT):
    ping_stats = quiet_ping(host, timeout=timeout, count=count)
    if DEBUG: print ping_stats
    assert ping_stats[0] < THRESHOLD
    return ping_stats[0]


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def get_stations():
    stations = 0
    try:
        result = run_shell_cmd(['/bin/bash', '%s/scripts/list-stations.sh' % WORKDIR])
        if result[0] == 0: stations = int(result[1].strip('\n'))
    except Exception as e:
        print repr(e)
        if DEBUG: print_exc()
        pass

    return stations


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def resolve_dns(host='us.%s' % DNS_HOST, record='A', family=4):
    res = None
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers=DNS_SERVERS
        if family == 6: resolver.nameservers=DNS6_SERVERS
        answers = dns.resolver.query(host, record)
        for rdata in answers:
            res = rdata.to_text() # always last record

        # fudge to make dns.resolver work with Nuitka compiled code
        pat = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        if not pat.match(res):
            addr_long = int(res.split(' ')[2], 16)
            res = socket.inet_ntoa(struct.pack('>L', addr_long))

        return res
        
    except dns.resolver.NoAnswer:
        return None
    

@retry(Exception, cdata='method=%s()' % stack()[0][3])
def run_speedtest(guid=GUID):
    server = '%s.1' % '.'.join(get_ip_address(TUN_IFACE).split('.')[:-1])

    cmd = ['/usr/bin/iperf', '--client', server,
           '--print_mss', '--nodelay', '--dualtest']

    if DEBUG: print cmd

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1,
              close_fds=ON_POSIX, env=os.environ.copy())

    queue = Queue()
    thread = Thread(target=enqueue_output, args=(p.stdout, queue))
    thread.daemon = True
    thread.start()

    return queue, p


@retry(Exception, cdata='method=%s()' % stack()[0][3])
def decode_jwt_payload(encoded=None):
    payload = dict()
    try:
        hdr = jwt.encode({}, '', algorithm='HS256').split('.')[0]
        sig = jwt.encode({}, '', algorithm='HS256').split('.')[2]
        payload = jwt.decode('%s.%s.%s' % (hdr, encoded, sig), verify=False)
        if DEBUG: print '%r: hdr=%r sig=%r payload=%r' % (stack()[0][3], hdr, sig, payload)
    except Exception as e:
        payload = dict()

    try:
        payload['u'] = socket.inet_ntoa(struct.pack('!L', int(payload['u'])))
    except Exception as e:
        pass
    
    return payload
