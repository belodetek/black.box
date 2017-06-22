#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, os, re, inspect
from threading import Thread
from traceback import print_exc
from inspect import stack
from time import sleep, time
from Queue import Empty

from common import (retry, log)

from api import (get_alpha, get_node_by_guid, get_node_by_country,
                 dequeue_speedtest, update_speedtest)

from utils import (resolve_dns, get_stations, get_ip_address, ping_host,
                   run_speedtest)

from vpn import (OPENVPN_BINARY, OPENVPN_VERSION, log_server_stats,
                 log_client_stats, _get_server_conns, _get_status,
                 connect_node, start_server, reauthenticate_clients,
                 enqueue_output, disconnect_clients)

from config import (POLL_FREQ, DEVICE_TYPE, GUID, THRESHOLD, DEBUG, UPNP,
                    LOOP_CYCLE, LOOP_TIMER, TUN_PROTO, TUN_MGMT, SUPPRESS_TS,
                    MGMT_IFACE, AF, AP, BITCOIN_PAYMENT_CHECK, TARGET_COUNTRY,
                    SERVER_DEVICE_TYPES, DNS_SUB_DOMAIN, CLIENT_DEVICE_TYPES)


def main():
    auth_thread = Thread()
    kill_thread = Thread()
    connected = False
    connecting = False
    c_gwip = None
    c_loss = 0
    c_proc = None
    c_proto = None
    c_pid = None
    c_stdoutq = None
    c_stderrq = None
    c_msg = None
    c_lineout = None
    c_lineerr = None
    c_status_line = None
    c_timer = 0
    now = time()
    c_stl = None
    c_str = list()
    c_stq = None
    c_stp = None
    c_remote = None
    c_country = TARGET_COUNTRY
    w_clnts = 0
    started = [False, False] # [udp, tcp]
    starting = [False, False]
    s_local = [None, None]
    s_loss = [0, 0]
    s_conns = [0, 0]
    s_proc = [None, None]
    s_pid = [None, None]
    s_stdoutq = [None, None]
    s_stderrq = [None, None]
    s_msg = [None, None]
    s_lineout = [None, None]
    s_lineerr = [None, None]
    s_status_line = None
    
    if SUPPRESS_TS:
        p1 = re.compile('^(.*)$')   
    else:
        p1 = re.compile('^([\w]{3}) ([\w]{3}) ([\d]{1,2}) ([\d]+:[\d]+:[\d]+) ([\d]{4}) (.*)$')
    group = p1.groups - 1
        
    if bool(re.search('^2.3.', OPENVPN_VERSION)):
        p2 = re.compile('^.* dev ([\w\d]+) local ([\d]+\.[\d]+\.[\d]+\.[\d]+) peer ([\d]+\.[\d]+\.[\d]+\.[\d]+)$')

    if bool(re.search('^2.4.', OPENVPN_VERSION)):
        p2 = re.compile('^.*ifconfig ([\w\d]+) ([\d]+\.[\d]+\.[\d]+\.[\d]+) pointopoint ([\d]+\.[\d]+\.[\d]+\.[\d]+) mtu [\d]+$')

    if DEVICE_TYPE == 5:
        p2 = re.compile('^.*get_ping_host: route_network_[0-9]+=([\d]+\.[\d]+\.[\d]+\.[\d]+)$')
        p3 = re.compile('^.*remote=(.*) country=(.*)$')

    mgmt_ipaddr = None
    if TUN_MGMT: mgmt_ipaddr = get_ip_address(MGMT_IFACE)

    while True:
        try:            
            if DEVICE_TYPE == 0:
                log('%r: device=%r' % (stack()[0][3], GUID))
                sys.exit(0)

            if DEBUG: print 'os.environ: %r' % os.environ

            for i in xrange(0, LOOP_CYCLE):
                ###########################
                # server mode(s) or mixed #
                ###########################
                if DEVICE_TYPE in [1, 3, 4]:                    
                    s_lineout = [None, None]
                    s_msg[0] = None
                    s_msg[1] = None
                    for idx, proto in enumerate(TUN_PROTO):
                        if DEBUG:
                            s_lineerr = [None, None]
                            if s_stderrq[idx]:
                                try:
                                    s_lineerr[idx] = s_stderrq[idx].get(timeout=LOOP_TIMER / 4)
                                    log('%r: %r' % (proto, s_lineerr[idx]))
                                except Empty:
                                    pass
                  
                        if s_stdoutq[idx]:
                            try:
                                s_lineout[idx] = s_stdoutq[idx].get(timeout=LOOP_TIMER / 2)
                                log('%r: %r' % (proto, s_lineout[idx]))
                            except Empty:
                                pass
       
                        try:
                            m1 = p1.search(s_lineout[idx])
                            if m1: s_msg[idx] = m1.group(group)
                        except TypeError:
                            pass

                        if s_msg[idx] in ['Initialization Sequence Completed']:
                            started[idx] = True
                            starting[idx] = False
                            
                            try:
                                log_server_stats(status=started)
                            except Exception as e:
                                print repr(e)
                                if DEBUG: print_exc()
                                pass

                        try:
                            m2 = p2.search(s_msg[idx]).groups()
                            dev = m2[0]
                            s_local[idx] = m2[1]
                            s_peer = m2[2]
                            log('%r: iface=%r local=%r peer=%r proto=%r' % (stack()[0][3],
                                                                            dev, s_local[idx],
                                                                            s_peer, proto))
                        except (TypeError, AttributeError):
                            pass

                        if not started[idx] and starting[idx]:
                            if i % LOOP_CYCLE == 0 and not started[idx]:
                                log('%r: started=%r starting=%r proto=%r s_pid=%r' % (stack()[0][3], started[idx],
                                                                                      starting[idx], proto, s_pid[idx]))
                                started[idx] = False
                                starting[idx] = False
                                s_proc[idx].terminate()
                                s_pid[idx] = None
                                
                        if not started[idx] and not starting[idx]:
                            if i % LOOP_CYCLE == 0: # once per loop
                                starting[idx] = True
                                log('%r: starting=%r proto=%r' % (stack()[0][3],
                                                                  starting[idx], proto))
                                
                                try:
                                    (s_stdoutq[idx], s_stderrq[idx], s_proc[idx]) = start_server(proto=proto)
                                    s_pid[idx] = s_proc[idx].pid
                                except Exception as e:
                                    starting[idx] = False
                                    print repr(e)
                                    if DEBUG: print_exc()
                                   
                        if started[idx] and not starting[idx]:
                            if not kill_thread.isAlive():
                                    kill_thread = Thread(target=disconnect_clients, args=())
                                    kill_thread.daemon = True
                                    kill_thread.start()
                                    log('disconnect_clients: name=%r alive=%r daemon=%r' % (kill_thread.name,
                                                                                            kill_thread.isAlive(),
                                                                                            kill_thread.isDaemon()))

                            if not auth_thread.isAlive():
                                if BITCOIN_PAYMENT_CHECK:
                                    auth_thread = Thread(target=reauthenticate_clients, args=())
                                    auth_thread.daemon = True
                                    auth_thread.start()
                                    log('reauthenticate_clients: name=%r alive=%r daemon=%r' % (auth_thread.name,
                                                                                                auth_thread.isAlive(),
                                                                                                auth_thread.isDaemon()))
                                                        
                            if i % LOOP_CYCLE == 0:
                                if DEBUG: log('get_status(%r): %r' % (proto, _get_status(proto=proto)))
                                s_conns[idx] = int(_get_server_conns(proto=proto))
                                
                            if i % POLL_FREQ == 0 and s_local[idx]: # every x cycles per loop
                                s_loss[idx] = 100
                                try:
                                    s_loss[idx] = ping_host(host=s_local[idx])
                                except AssertionError as e:
                                    print repr(e)
                                    if DEBUG: print_exc()
                                    log('%r: proto=%r s_local=%r s_loss=%r' % (stack()[0][3],
                                                                               proto, s_local[idx],
                                                                               s_loss[idx]))
                                    started[idx] = False
                                    starting[idx] = False
                                    s_proc[idx].terminate()
                                    s_loss[idx] = 0
                                    break

                        if not (DEBUG and s_stderrq[idx]) and not s_stdoutq[idx]:
                            sleep(LOOP_TIMER)

                    if i % LOOP_CYCLE == 0:
                        try:
                            log_server_stats(status=started)
                        except Exception as e:
                            print repr(e)
                            if DEBUG: print_exc()
                            pass
                
                        s_status_line = '%r: started=%r starting=%r af=%r ip=%r loss=%r pid=%r conns=%r mgmt_tun=%r hostapd=%r upnp=%r' % (stack()[0][3], started, starting,
                                                                                                                                           AF, s_local, s_loss,
                                                                                                                                           s_pid, s_conns,
                                                                                                                                           mgmt_ipaddr, AP, UPNP)
                        log(s_status_line)
                        
                ###########################
                # client mode(s) or mixed #
                ###########################
                if DEVICE_TYPE in [2, 3, 5]:
                    if c_stp and now - c_timer > (LOOP_TIMER * LOOP_CYCLE * 5):
                        log('%r: pid=%r elapsed=%r' % (stack()[0][3], c_stp.pid, now - c_timer))
                        c_stp.terminate()
                        c_stp = None
                        c_stq = None
                        c_timer = 0
                        c_str = list()
                        result = {'status': 1, 'down': None, 'up': None}
                        log('run_speedtest: result=%r' % result)

                        try:
                            res = update_speedtest(data=result)
                            log('update_speedtest(%r): %r' % (res[0], res[1]))
                        except Exception as e:
                            print repr(e)
                            if DEBUG: print_exc()
                            pass
                            
                    if DEBUG:
                        c_lineerr = None
                        if c_stderrq:
                            try:
                                c_lineerr = c_stderrq.get(timeout=LOOP_TIMER)
                                log(c_lineerr)
                            except Empty:
                                pass

                    c_lineout = None
                    if c_stdoutq:
                        try:
                            c_lineout = c_stdoutq.get(timeout=LOOP_TIMER / 2)
                            log(c_lineout)
                        except Empty:
                            pass

                    c_stl = None
                    if c_stq:
                        try:
                            c_stl = c_stq.get(timeout=LOOP_TIMER / 2)
                            log(c_stl)
                            c_str.append(c_stl)
                        except Empty:
                            pass

                    if len(c_str) == 15: # hack (iperf --dualtest)
                        down = [el for el in c_str[-4].split(' ') if el]
                        up = [el for el in c_str[-2].split(' ') if el]

                        result = {'status': 0,
                                  'down': ' '.join([s for s in down[2:] if s]),         
                                  'up': ' '.join([s for s in up[2:] if s])}

                        log('run_speedtest: result=%r' % result)

                        try:
                            res = update_speedtest(data=result)
                            log('update_speedtest(%r): %r' % (res[0], res[1]))
                        except Exception as e:
                            print repr(e)
                            if DEBUG: print_exc()
                            pass

                        c_str = list()
                        c_timer = 0
                        c_stp = None
                        c_stq = None
     
                    c_msg = None
                                    
                    try:
                        m1 = p1.search(c_lineout)
                        if m1: c_msg = m1.group(group)
                    except TypeError:
                        pass

                    if c_msg in ['SIGTERM[soft,tls-error] received, process exiting',
                                 'SIGUSR1[soft,init_instance] received, process restarting',
                                 'SIGUSR1[soft,connection-reset] received, process restarting',
                                 'SIGTERM[hard,] received, process exiting',
                                 'Exiting due to fatal error']:
                        
                        log('terminate: c_pid=%r' % c_pid)
                        connected = False
                        connecting = False
                        c_proc.terminate()
                        c_pid = None

                    if c_msg in ['Initialization Sequence Completed']:
                        connected = True
                        connecting = False

                        try:
                            log_client_stats(status=connected, country=c_country)
                        except Exception as e:
                            print repr(e)
                            if DEBUG: print_exc()
                            pass

                    try:
                        m2 = p2.search(c_msg).groups()
                        dev = m2[0]
                        c_local = m2[1]
                        c_peer = m2[2]
                        c_gwip = c_peer.split('.')
                        c_gwip[3] = '1'
                        c_gwip = '.'.join(c_gwip)
                        log('%r: iface=%r local=%r peer=%r gwip=%r family=%r' % (stack()[0][3],
                                                                                 dev, c_local,
                                                                                 c_peer, c_gwip, AF))
                    except (TypeError, AttributeError):
                        pass
                    
                    if DEVICE_TYPE == 5:
                        try:
                            m3 = p3.search(c_msg).groups()
                            c_remote = m3[0]
                            c_country = m3[1]
                            log('%r: remote=%r country=%r' % (stack()[0][3],
                                                              c_remote, c_country))
                        except (TypeError, AttributeError):
                            pass

                    if not connected and connecting:
                        if i % LOOP_CYCLE == 0 and not connected:
                            log('%r: connected=%r connecting=%r c_pid=%r' % (stack()[0][3], connected,
                                                                             connecting, c_pid))
                            connected = False
                            connecting = False
                            c_proc.terminate()
                            c_pid = None
                            
                    if not connected and not connecting:
                        if i % LOOP_CYCLE == 0:
                            connecting = True
                            log('%r: connecting=%r family=%r' % (stack()[0][3],
                                                                 connecting, AF))

                            try:
                                (c_stdoutq, c_stderrq, c_proc, c_proto) = connect_node(family=AF)
                                c_pid = c_proc.pid
                            except AssertionError as e:
                                connecting = False
                                print repr(e)
                                if DEBUG: print_exc()

                    if connected and not connecting:
                        if i % LOOP_CYCLE == 0:
                            try:
                                if not c_timer and dequeue_speedtest():
                                    c_timer = now
                                    c_str = list()
                                    (c_stq, c_stp) = run_speedtest()
                            except Exception as e:
                                print repr(e)
                                if DEBUG: print_exc()

                            if c_timer:
                                log('run_speedtest: pid=%r elapsed=%r results=%r' % (c_stp.pid, now - c_timer, len(c_str)))

                        if i % POLL_FREQ == 0 and c_gwip:
                            c_loss = 100
                            try:
                                c_loss = ping_host(host=c_gwip)
                            except AssertionError as e:
                                print repr(e)
                                if DEBUG: print_exc()
                                log('%r: c_gwip=%r c_loss=%r' % (stack()[0][3], c_gwip, c_loss))
                                connected = False
                                connecting = False
                                c_proc.terminate()
                                c_loss = 0
                                c_pid = None
                                break

                    if i % LOOP_CYCLE == 0:
                        try:
                            log_client_stats(status=connected, country=c_country)
                        except Exception as e:
                            print repr(e)
                            if DEBUG: print_exc()
                            pass
                        
                        w_clnts = get_stations()
                        
                        c_status_line = '%r: connected=%r connecting=%r af=%r ip=%r loss=%r pid=%r clients=%r proto=%r mgmt_tun=%r hostapd=%r upnp=%r' % (stack()[0][3], connected, connecting,
                                                                                                                                                          AF, c_gwip, c_loss, c_pid,
                                                                                                                                                          w_clnts, c_proto,
                                                                                                                                                          mgmt_ipaddr, AP, UPNP)
                        log(c_status_line)
                        now = time()

                    if not (DEBUG and c_stderrq) and not (c_stdoutq and c_stq):
                        sleep(LOOP_TIMER)

        except Exception as e:
            print repr(e)
            if DEBUG: print_exc()
            sleep(LOOP_CYCLE * LOOP_TIMER) # pause for full loop cycle
            pass

        finally:
            pass

    
if __name__ == '__main__':
    main()
