#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import inspect

from threading import Thread
from traceback import print_exc
from inspect import stack
from time import sleep, time
from queue import Empty
from common import retry, log
from api import *
from utils import *
from vpn import *
from config import *


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
	c_stimer = 0
	c_iotimer = 0
	now = time()
	c_stl = None
	c_str = list()
	c_stq = None
	c_stp = None
	c_iotl = None
	c_iotq = None
	c_iotp = None
	c_iott = None
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
		p1 = re.compile(
			'^([\w]{3}) ([\w]{3}) ([\d]{1,2}) ([\d]+:[\d]+:[\d]+) ([\d]{4}) (.*)$'
		)
	group = p1.groups - 1

	if bool(re.search('^2\.3\.', OPENVPN_VERSION)):
		p2 = re.compile(
			'^.* dev ([\w\d]+) local ([\d]+\.[\d]+\.[\d]+\.[\d]+) peer ([\d]+\.[\d]+\.[\d]+\.[\d]+)$'
		)

	if bool(re.search('^(2\.4\.|2\.5\.)', OPENVPN_VERSION)):
		p2 = re.compile(
			'^.*ifconfig ([\w\d]+) ([\d]+\.[\d]+\.[\d]+\.[\d]+) pointopoint ([\d]+\.[\d]+\.[\d]+\.[\d]+) mtu [\d]+$'
		)

	if DEVICE_TYPE == 5:
		p2 = re.compile(
			'^.*get_ping_host: route_network_[0-9]+=([\d]+\.[\d]+\.[\d]+\.[\d]+)$'
		)
		p3 = re.compile('^.*remote=(.*) country=(.*)$')

	# hdparm tests
	p4 = re.compile(
		'^\s+(.*):\s+(\d+\s+.*)\s+in\s+([\d\.]+\s+.*)\s+=\s+(.*)\n$'
	)

	# dd write
	p5 = re.compile(
		'^(\d+\s+.*)\s+\((.*),.*\)\s+.*,\s+(.*),\s+(.*)$'
	)

	mgmt_ipaddr = None
	if TUN_MGMT: mgmt_ipaddr = get_ip_address(MGMT_IFACE)

	while True:
		if DEVICE_TYPE == 0:
			log('{}: device={}'.format(stack()[0][3], GUID))
			sys.exit(0)

		if DEBUG: print('os.environ: {}'.format(os.environ))

		for i in range(1, LOOP_CYCLE + 1):
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
								s_lineerr[idx] = s_stderrq[idx].get(
									timeout=LOOP_TIMER
								).decode()
								log('{}: {}'.format(proto, s_lineerr[idx]))
							except Empty:
								pass
					else:
						if s_stderrq[idx]:
							with s_stderrq[idx].mutex:
								s_stderrq[idx].queue.clear()

					if s_stdoutq[idx]:
						try:
							s_lineout[idx] = s_stdoutq[idx].get(
								timeout=LOOP_TIMER
							).decode()
							log('{}: {}'.format(proto, s_lineout[idx]))
						except Empty:
							pass
					try:
						m1 = p1.search(s_lineout[idx])
						if m1: s_msg[idx] = m1.group(group)
					except (IndexError, TypeError, AttributeError):
						pass

					if s_msg[idx] in ['Initialization Sequence Completed']:
						started[idx] = True
						starting[idx] = False
						try:
							log_server_stats(status=started)
						except:
							if DEBUG: print_exc()
					try:
						m2 = p2.search(s_msg[idx]).groups()
						dev = m2[0]
						s_local[idx] = m2[1]
						s_peer = m2[2]
						log(
							'{}: iface={} local={} peer={} proto={}'.format(
								stack()[0][3],
								dev,
								s_local[idx],
								s_peer,
								proto
							)
						)
					except (IndexError, TypeError, AttributeError):
						pass

					if not started[idx] and starting[idx]:
						if i % LOOP_CYCLE == 0 and not started[idx]:
							log(
								'{}: cycle={} started={} starting={} proto={} s_pid={}'.format(
									stack()[0][3],
									i,
									started[idx],
									starting[idx],
									proto,
									s_pid[idx]
								)
							)
							started[idx] = False
							starting[idx] = False
							s_proc[idx].terminate()
							s_pid[idx] = None

					if not started[idx] and not starting[idx]:
						if i == 1: # once per loop (start)
							starting[idx] = True
							log(
								'{}: cycle={} starting={} proto={}'.format(
									stack()[0][3],
									i,
									starting[idx],
									proto
								)
							)

							try:
								(s_stdoutq[idx], s_stderrq[idx], s_proc[idx]) = start_server(
									proto=proto
								)
								s_pid[idx] = s_proc[idx].pid
							except Exception as e:
								starting[idx] = False
								print(repr(e))
								if DEBUG: print_exc()

					if started[idx] and not starting[idx]:
						if not kill_thread.isAlive():
								kill_thread = Thread(
									target=disconnect_clients,
									args=()
								)
								kill_thread.daemon = True
								kill_thread.start()
								log(
									'disconnect_clients: name={} alive={} daemon={}'.format(
										kill_thread.name,
										kill_thread.isAlive(),
										kill_thread.isDaemon()
									)
								)

						if not auth_thread.isAlive():
							if BITCOIN_PAYMENT_CHECK:
								auth_thread = Thread(
									target=reauthenticate_clients,
									args=()
								)
								auth_thread.daemon = True
								auth_thread.start()
								log(
									'reauthenticate_clients: name={} alive={} daemon={}'.format(
										auth_thread.name,
										auth_thread.isAlive(),
										auth_thread.isDaemon()
									)
								)

						if i == 1 or i % LOOP_CYCLE == 0: # twice per loop (start and end)
							if DEBUG: log(
								'get_status: cycle={} proto={} status={}'.format(
									i,
									proto,
									get_status(proto=proto)
								)
							)
							s_conns[idx] = int(
								get_server_conns_by(
									proto=proto
								)
							)

						if i % POLL_FREQ == 0 and s_local[idx]: # every x cycles per loop
							s_loss[idx] = 100
							try:
								s_loss[idx] = ping_host(host=s_local[idx])
							except AssertionError as e:
								print(repr(e))
								if DEBUG: print_exc()
								log(
									'{}: cycle={} proto={} s_local={} s_loss={}'.format(
										i,
										stack()[0][3],
										proto,
										s_local[idx],
										s_loss[idx]
									)
								)
								started[idx] = False
								starting[idx] = False
								s_proc[idx].terminate()
								s_loss[idx] = 0
								break

					# flush the stderr queue if not debugging
					if not DEBUG and s_stderrq[idx]:
						with s_stderrq[idx].mutex:
							s_stderrq[idx].queue.clear()

				if i % LOOP_CYCLE == 0:
					if DEVICE_TYPE == 3: # test if double-vpn is up
						try:
							shell_check_output_cmd(
								'ip link | grep %s' % TUN_IFACE
							)
							gwip = shell_check_output_cmd(
								"ip route | grep %s | grep -E '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ via [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ dev %s' | awk '{print $1}'" % (
									TUN_IFACE,
									TUN_IFACE
								)
							)
							log(
								'iface={} gwip={}'.format(
									TUN_IFACE,
									gwip
								)
							)
							ping_host(
								host=gwip.strip('\n'),
								timeout=1,
								count=3
							)
							try:
								# server up only if double-vpn is up
								log_server_stats(status=started)
							except:
								if DEBUG: print_exc()
						except:
							if DEBUG: print_exc()
							log(
								'{}: double-vpn not ready'.format(
									stack()[0][3]
								)
							)
							try:
								# force server down if double-vpn is down
								log_server_stats()
							except:
								if DEBUG: print_exc()
					else:
						try:
							log_server_stats(status=started)
						except:
							if DEBUG: print_exc()

					s_status_line = '{}: cycle={} started={} starting={} ip={} loss={} pid={} conns={} mgmt_tun={} af={} hostapd={} upnp={}'.format(
						stack()[0][3],
						i,
						started,
						starting,
						s_local,
						s_loss,
						s_pid,
						s_conns,
						mgmt_ipaddr,
						AF,
						AP,
						UPNP
					)
					log(s_status_line)

			###########################
			# client mode(s) or mixed #
			###########################
			if DEVICE_TYPE in [2, 3, 5]:
				# iperf timeout
				if c_stp and now - c_stimer > (LOOP_TIMER * LOOP_CYCLE * 5):
					log(
						'{}: pid={} elapsed={}'.format(
							stack()[0][3],
							c_stp.pid,
							now - c_stimer
						)
					)
					c_stp.terminate()
					c_stp = None
					c_stq = None
					c_stimer = 0
					c_str = list()

					result = {
						'status': 1,
						'down': None,
						'up': None
					}
					log('run_speedtest: result={}'.format(result))
					try:
						res = update_speedtest(data=result)
						log('update_speedtest: {}'.format(res))
					except Exception as e:
						print(repr(e))
						if DEBUG: print_exc()

				# hdparm or dd timeout
				if c_iotp and now - c_iotimer > (LOOP_TIMER * LOOP_CYCLE * 3):
					log(
						'{}: pid={} elapsed={} test={}'.format(
							stack()[0][3],
							c_iotp.pid,
							now - c_iotimer,
							c_iott
						)
					)
					try:
						result = {
							'status': 1,
							'test': c_iott,
							'result': None
						}
						log('run_iotest: result={}'.format(result))
						res = update_iotest(data=result)
						log(
							'update_iotest({}): {}'.format(
								res[0],
								res[1]
							)
						)
					except Exception as e:
						print(repr(e))
						if DEBUG: print_exc()
					c_iotp.terminate()
					c_iotp = None
					c_iotq = None
					c_iotimer = 0
					c_iott = None

				if DEBUG:
					c_lineerr = None
					if c_stderrq:
						try:
							c_lineerr = c_stderrq.get(timeout=LOOP_TIMER).decode()
							log(c_lineerr)
						except Empty:
							pass
				else:
					if c_stderrq:
						with c_stderrq.mutex:
							c_stderrq.queue.clear()

				c_lineout = None
				if c_stdoutq:
					try:
						c_lineout = c_stdoutq.get(timeout=LOOP_TIMER).decode()
						log(c_lineout)
					except Empty:
						pass

				c_stl = None
				if c_stq:
					try:
						c_stl = c_stq.get(timeout=LOOP_TIMER).decode()
						log(c_stl)
						c_str.append(c_stl)
					except Empty:
						pass

				# speedtest result
				if len(c_str) >= 13: # lines of output hack (iperf --dualtest)
					result = {
						'status': 0
					}

					try:
						down = [el for el in c_str[-2].split(' ') if el]
						result['down'] = ' '.join([s for s in down[2:] if s])
					except:
						result['down'] = 'N/A'

					try:
						up = [el for el in c_str[-1].split(' ') if el]
						result['up'] = ' '.join([s for s in up[2:] if s])
					except:
						result['up'] = 'N/A'

					log('run_speedtest: result={}'.format(result))

					try:
						res = update_speedtest(data=result)
						log('update_speedtest: {}'.format(res))
					except Exception as e:
						print(repr(e))
						if DEBUG: print_exc()

					c_str = list()
					c_stimer = 0
					c_stp = None
					c_stq = None

				# hdparm or dd result
				c_iotl = None
				if c_iotq:
					try:
						c_iotl = c_iotq.get(timeout=LOOP_TIMER).decode()
						log(c_iotl)
						if p4.search(c_iotl) or p5.search(c_iotl):
							result = {
								'status': 0,
								'test': c_iott,
								'result': c_iotl.lstrip().rstrip().strip('\n')
							}
							log('run_iotest: result={}'.format(result))
							try:
								res = update_iotest(data=result)
								log(
									'update_iotest({}): {}'.format(
										res[0],
										res[1]
									)
								)
							except Exception as e:
								print(repr(e))
								if DEBUG: print_exc()
							c_iotimer = 0
							c_iott = None
							c_iotp = None
							c_iotq = None
					except Empty:
						pass

				c_msg = None
				try:
					m1 = p1.search(c_lineout)
					if m1: c_msg = m1.group(group)
				except (IndexError, TypeError, AttributeError):
					pass

				if c_msg in [
					'SIGTERM[soft,tls-error] received, process exiting',
					'SIGUSR1[soft,init_instance] received, process restarting',
					'SIGUSR1[soft,connection-reset] received, process restarting',
					'SIGTERM[hard,] received, process exiting',
					'Exiting due to fatal error'
				]:
					log('terminate: c_pid={}'.format(c_pid))
					connected = False
					connecting = False
					c_proc.terminate()
					c_pid = None

				if c_msg in ['Initialization Sequence Completed']:
					connected = True
					connecting = False
					try:
						log_client_stats(
							status=connected,
							country=c_country
						)
					except:
						if DEBUG: print_exc()
				try:
					m2 = p2.search(c_msg).groups()
					dev = m2[0]
					c_local = m2[1]
					c_peer = m2[2]
					c_gwip = c_peer.split('.')
					c_gwip[3] = '1'
					c_gwip = '.'.join(c_gwip)
					log(
						'{}: iface={} local={} peer={} gwip={} family={}'.format(
							stack()[0][3],
							dev,
							c_local,
							c_peer,
							c_gwip,
							AF
						)
					)
				except (IndexError, TypeError, AttributeError):
					pass

				if DEVICE_TYPE == 5:
					try:
						m3 = p3.search(c_msg).groups()
						c_remote = m3[0]
						c_country = m3[1]
						log(
							'{}: remote={} country={}'.format(
								stack()[0][3],
								c_remote,
								c_country
							)
						)
					except (IndexError, TypeError, AttributeError):
						pass

				if not connected and connecting:
					if i % LOOP_CYCLE == 0 and not connected:
						log(
							'{}: cycle={} connected={} connecting={} c_pid={}'.format(
								stack()[0][3],
								i,
								connected,
								connecting,
								c_pid
							)
						)
						connected = False
						connecting = False
						c_proc.terminate()
						c_pid = None

				if not connected and not connecting:
					if i == 1:
						connecting = True
						log(
							'{}: cycle={} connecting={} family={}'.format(
								stack()[0][3],
								i,
								connecting,
								AF
							)
						)
						try:
							(c_stdoutq, c_stderrq, c_proc, c_proto) = connect_node(
								family=AF
							)
							c_pid = c_proc.pid
						except AssertionError as e:
							connecting = False
							print(repr(e))
							if DEBUG: print_exc()

				if connected and not connecting:
					if i % LOOP_CYCLE == 0:
						# run speedtest
						try:
							if not c_stimer and dequeue_speedtest():
								c_stimer = now
								c_str = list()
								(c_stq, c_stp) = run_speedtest()
						except Exception as e:
							print(repr(e))
							if DEBUG: print_exc()
						if c_stimer:
							log(
								'run_speedtest: pid={} elapsed={} results={}'.format(
									c_stp.pid,
									now - c_stimer,
									len(c_str)
								)
							)

						# run hdparm or dd
						try:
							try:
								c_iott = dequeue_iotest()
							except:
								c_iott = None
							if DEBUG:
								log('dequeue_iotest: test={}'.format(c_iott))
							if not c_iotimer and c_iott in IOTESTS:
								c_iotimer = now
								(c_iotq, c_iotp) = run_iotest(test=c_iott)
						except Exception as e:
							print(repr(e))
							if DEBUG: print_exc()
						if c_iotimer:
							log(
								'run_iotest: pid={} elapsed={} test={} result={}'.format(
									c_iotp.pid,
									now - c_iotimer,
									c_iott,
									c_iotl
								)
							)

					if i % POLL_FREQ == 0 and c_gwip:
						c_loss = 100
						try:
							c_loss = ping_host(host=c_gwip)
						except AssertionError as e:
							print(repr(e))
							if DEBUG: print_exc()
							log(
								'{}: c_gwip={} c_loss={}'.format(
									stack()[0][3],
									c_gwip,
									c_loss
								)
							)
							connected = False
							connecting = False
							c_proc.terminate()
							c_loss = 0
							c_pid = None
							break

				if i % LOOP_CYCLE == 0:
					try:
						log_client_stats(
							status=connected,
							country=c_country
						)
					except:
						if DEBUG: print_exc()

					w_clnts = get_stations()
					c_status_line = '{}: cycle={} connected={} connecting={} proto={} ip={} loss={} pid={} clients={} mgmt_tun={} af={} hostapd={} upnp={}'.format(
						stack()[0][3],
						i,
						connected,
						connecting,
						c_proto,
						c_gwip,
						c_loss,
						c_pid,
						w_clnts,
						mgmt_ipaddr,
						AF,
						AP,
						UPNP
					)
					log(c_status_line)
					now = time()

				# flush the stderr queue if not debugging
				if not DEBUG and c_stderrq:
					with c_stderrq.mutex: c_stderrq.queue.clear()

				sleep(LOOP_TIMER)


if __name__ == '__main__':
	main()
