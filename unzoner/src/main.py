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
	magic_lines = ['Initialization Sequence Completed']
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
	s_conns = [0, 0]
	s_proc = [None, None]
	s_pid = [None, None]
	s_stdoutq = [None, None]
	s_stderrq = [None, None]
	s_msg = [None, None]
	s_lineout = [None, None]
	s_lineerr = [None, None]
	s_status_line = None
	this = stack()[0][3]

	if SUPPRESS_TS:
		p1 = re.compile('^(.*)$')
	else:
		p1 = re.compile(
			'^([\w]{3}) ([\w]{3}) ([\d]{1,2}) ([\d]+:[\d]+:[\d]+) ([\d]{4}) (.*)$'
		)
	group = p1.groups - 1

	# for information only
	p2 = re.compile('^.*remote=(.*) country=(.*)$')

	# (iotest) hdparm tests
	p3 = re.compile(
		'^\s+(.*):\s+(\d+\s+.*)\s+in\s+([\d\.]+\s+.*)\s+=\s+(.*)\n$'
	)

	# (iotest) dd write
	p4 = re.compile(
		'^(\d+\s+.*)\s+\((.*),.*\)\s+.*,\s+(.*),\s+(.*)$'
	)

	if DEBUG: print('os.environ: {}'.format(os.environ))

	while True:
		if DEVICE_TYPE == 0: # disabled
			log('{}: device={}'.format(this, GUID))
			sys.exit(0)

		for i in range(1, LOOP_CYCLE + 1): # clunky event loop
			###########################
			# server mode(s) or mixed #
			###########################
			if DEVICE_TYPE in [1, 3, 4]: # 1:server 2:unblocking 3:server-mixed 4:private 5:VPN
				s_lineout = [None, None]
				s_msg[0] = None
				s_msg[1] = None
				for idx, proto in enumerate(TUN_PROTO):
					if DEBUG:
						s_lineerr = [None, None]
						if s_stderrq[idx]:
							try:
								s_lineerr[idx] = s_stderrq[idx].get(timeout=LOOP_TIMER).decode()
								log('{}: {}'.format(proto, s_lineerr[idx]))
							except Empty:
								pass
					else:
						if s_stderrq[idx]:
							with s_stderrq[idx].mutex: s_stderrq[idx].queue.clear()

					if s_stdoutq[idx]:
						try:
							s_lineout[idx] = s_stdoutq[idx].get(timeout=LOOP_TIMER).decode()
							log('{}: {}'.format(proto, s_lineout[idx]))
						except Empty:
							pass
					try:
						m1 = p1.search(s_lineout[idx])
						if m1: s_msg[idx] = m1.group(group)
					except (IndexError, TypeError, AttributeError):
						pass

					if s_msg[idx] in magic_lines:
						started[idx] = True
						starting[idx] = False
						log_server_stats(status=started)

					if not started[idx] and not starting[idx]:
						if i == 1: # at the beginning of the cycle
							starting[idx] = True
							log('vpn-server-state: cycle={} starting={} proto={}'.format(
								i,
								starting[idx],
								proto
							))

							try:
								(s_stdoutq[idx], s_stderrq[idx], s_proc[idx]) = start_server(proto=proto)
								s_pid[idx] = s_proc[idx].pid
							except Exception as e:
								starting[idx] = False
								print('exception-handler in {}: {}'.format(this, repr(e)))
								if DEBUG: print_exc()

					if started[idx] and not starting[idx]:
						if not kill_thread.is_alive():
								kill_thread = Thread(target=disconnect_clients, args=())
								kill_thread.daemon = True
								kill_thread.start()
								log('disconnect_clients: name={} alive={} daemon={}'.format(
									kill_thread.name,
									kill_thread.is_alive(),
									kill_thread.daemon
								))

						if not auth_thread.is_alive():
							if BITCOIN_PAYMENT_CHECK:
								auth_thread = Thread(
									target=reauthenticate_clients,
									args=()
								)
								auth_thread.daemon = True
								auth_thread.start()
								log('(re)authenticate_clients: name={} alive={} daemon={}'.format(
									auth_thread.name,
									auth_thread.is_alive(),
									auth_thread.daemon
								))

						if i == 1 or i % LOOP_CYCLE == 0: # twice per loop (start and end)
							if DEBUG: log('vpn-server-state: cycle={} proto={} status={}'.format(
								i,
								proto,
								get_status(proto=proto)
							))
							s_conns[idx] = int(get_server_conns_by(proto=proto))

					# flush the stderr queue if not debugging
					if not DEBUG and s_stderrq[idx]:
						with s_stderrq[idx].mutex: s_stderrq[idx].queue.clear()

				if i % LOOP_CYCLE == 0: # at the end of the cycle
					try:
						assert started[idx] and not starting[idx] # if not started by now
					except:
						started[idx] = False
						starting[idx] = False
						s_proc[idx].terminate()
						while s_proc[idx].poll() is None: sleep(LOOP_TIMER) # https://stackoverflow.com/a/2996026/1559300
						s_pid[idx] = None

					if DEVICE_TYPE == 3 and connected: # test if client-vpn is up
						try:
							shell_check_output_cmd('ip link | grep {}'.format(TUN_IFACE)) # raises exception if tunnel is down
							log_server_stats(status=started) # server up only if client-vpn is up
						except:
							log_server_stats() # force server down if client-vpn is down
					else:
						log_server_stats(status=started)

					s_status_line = 'server-status: cycle={} started={} starting={} s_pid={} s_conns={} AF={} hostAPd={} UPNP={}'.format(
						i,
						started,
						starting,
						s_pid,
						s_conns,
						AF,
						AP,
						UPNP
					)
					log(s_status_line)

			###########################
			# client mode(s) or mixed #
			###########################
			if DEVICE_TYPE in [2, 3, 5]: # 1:server 2:unblocking 3:server-mixed 4:private 5:VPN
				# iperf timeout
				if c_stp and now - c_stimer > (LOOP_TIMER * LOOP_CYCLE * 5):
					log('iperf-status: pid={} elapsed={}'.format(
						c_stp.pid,
						now - c_stimer
					))
					c_stp.terminate()
					while c_stp.poll() is None: sleep(LOOP_TIMER)
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
						print('exception-handler in {}: {}'.format(this, repr(e)))
						if DEBUG: print_exc()

				# hdparm or dd timeout
				if c_iotp and now - c_iotimer > (LOOP_TIMER * LOOP_CYCLE * 3):
					log('iotest-status: pid={} elapsed={} test={}'.format(
						c_iotp.pid,
						now - c_iotimer,
						c_iott
					))
					try:
						result = {
							'status': 1,
							'test': c_iott,
							'result': None
						}
						log('run_iotest: result={}'.format(result))
						res = update_iotest(data=result)
						log('update_iotest({}): {}'.format(res[0], res[1]))
					except Exception as e:
						print('exception-handler in {}: {}'.format(this, repr(e)))
						if DEBUG: print_exc()
					c_iotp.terminate()
					while c_iotp.poll() is None: sleep(LOOP_TIMER)
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
						with c_stderrq.mutex: c_stderrq.queue.clear()

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
						print('exception-handler in {}: {}'.format(this, repr(e)))
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
						if p3.search(c_iotl) or p4.search(c_iotl):
							result = {
								'status': 0,
								'test': c_iott,
								'result': c_iotl.lstrip().rstrip().strip('\n')
							}
							log('run_iotest: result={}'.format(result))
							try:
								res = update_iotest(data=result)
								log('update_iotest({}): {}'.format(res[0], res[1]))
							except Exception as e:
								print('exception-handler in {}: {}'.format(this, repr(e)))
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

				if c_msg in magic_lines:
					connected = True
					connecting = False
					log_client_stats(status=connected, country=c_country)

				if DEVICE_TYPE == 5:
					try:
						m3 = p2.search(c_msg).groups()
						c_remote = m3[0]
						c_country = m3[1]
						log('vpn-client-state: remote={} country={}'.format(
							this,
							c_remote,
							c_country
						))
					except (IndexError, TypeError, AttributeError):
						pass

				if not connected and not connecting: # connect client-vpn
					if i == 1: # at the beginning of the cycle
						connecting = True
						log('vpn-client-state: cycle={} connecting={} family={}'.format(
							i,
							connecting,
							AF
						))
						try:
							(c_stdoutq, c_stderrq, c_proc, c_proto) = connect_node(
								family=AF
							)
							c_pid = c_proc.pid
							connected = True
							connecting = False
						except AssertionError as e:
							connected = False
							connecting = False
							print('exception-handler in {}: {}'.format(this, repr(e)))
							if DEBUG: print_exc()

				if connected and not connecting:
					if i % LOOP_CYCLE == 0: # at the end of the cycle
						# run speedtest
						try:
							if not c_stimer and dequeue_speedtest():
								c_stimer = now
								c_str = list()
								(c_stq, c_stp) = run_speedtest()
						except Exception as e:
							print('exception-handler in {}: {}'.format(this, repr(e)))
							if DEBUG: print_exc()
						if c_stimer:
							log('run_speedtest: pid={} elapsed={} results={}'.format(
								c_stp.pid,
								now - c_stimer,
								len(c_str)
							))

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
							print('exception-handler in {}: {}'.format(this, repr(e)))
							if DEBUG: print_exc()
						if c_iotimer:
							log('run_iotest: pid={} elapsed={} test={} result={}'.format(
								c_iotp.pid,
								now - c_iotimer,
								c_iott,
								c_iotl
							))

				if i % LOOP_CYCLE == 0: # at the end of the cycle
					try:
						shell_check_output_cmd('ip link | grep {}'.format(TUN_IFACE)) # raises exception if tunnel is down
						geo_result = get_geo_location()
						assert geo_result, '{}: client tunnel down'.format(this)
						print('client-vpn-geo: {}'.format(geo_result))
						if DEVICE_TYPE == 3: log_server_stats(status=started) # server up only if client-vpn is up
					except Exception as e:
						print('exception-handler in {}: {}'.format(this, repr(e)))
						if DEBUG: print_exc()
						connected = False
						connecting = False
						c_proc.terminate()
						while c_proc.poll() is None: sleep(LOOP_TIMER)
						c_pid = None
						if DEVICE_TYPE == 3: log_server_stats() # force server down if clienv-vpn is down

					log_client_stats(status=connected, country=c_country)
					w_clnts = get_stations()
					c_status_line = 'client-status: cycle={} connected={} connecting={} c_proto={} c_pid={} w_clnts={} AF={} hostAPd={} UPNP={}'.format(
						i,
						connected,
						connecting,
						c_proto,
						c_pid,
						w_clnts,
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
