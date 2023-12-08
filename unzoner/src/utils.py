#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import fcntl
import struct
import re
import json
import jwt
import dns.resolver

from time import time, sleep
from inspect import stack
from subprocess import check_output, Popen, PIPE, STDOUT
from threading import Thread
from queue import Queue, Empty
from traceback import print_exc

from common import retry
from config import *


def shell_check_output_cmd(cmd):
	if DEBUG: print('{}: cmd={}'.format(stack()[0][3], cmd))
	return check_output(
		cmd,
		stderr=STDOUT,
		shell=True
	).decode()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def run_shell_cmd(cmd):
	if DEBUG: print('{}: cmd={}'.format(stack()[0][3], cmd))
	p = Popen(
		cmd,
		stdin=PIPE,
		stdout=PIPE,
		stderr=PIPE,
		bufsize=0,
		close_fds=ON_POSIX,
		env=os.environ.copy(),
		shell=False
	)
	output, err = p.communicate()
	return (p.returncode, output, err, p.pid)


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def run_background_shell_cmd(cmd):
	if DEBUG: print('{}: cmd={}'.format(stack()[0][3], cmd))
	p = Popen(
		cmd,
		stdin=PIPE,
		stdout=PIPE,
		stderr=PIPE,
		bufsize=0,
		close_fds=ON_POSIX,
		env=os.environ.copy(),
		shell=False
	)
	stat = p.poll()
	while stat == None:
		stat = p.poll()
	return p


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def run_shell_cmd_nowait(cmd):
	if DEBUG: print('{}: cmd={}'.format(stack()[0][3], cmd))
	p = Popen(
		cmd,
		stdin=PIPE,
		stdout=PIPE,
		stderr=PIPE,
		bufsize=0,
		close_fds=ON_POSIX,
		env=os.environ.copy(),
		shell=False
	)
	return p


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
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
					data.append(buffer.decode())
					# reset the begin time for measurement
					begin = time()
				else:
					sleep(LOOP_TIMER)
			except:
				pass

	except Exception as e:
		if DEBUG: print_exc()
	return ''.join(data)


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def enqueue_output(out, queue):
	for line in iter(out.readline, b''):
		queue.put(line)
	out.close()


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_hostname():
	hostname = 'localhost'
	try:
		hostname = socket.gethostname()
	except:
		pass
	return hostname


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_geo_location(family=AF):
	data = dict()
	cmd = [
		'curl',
		'-{}'.format(family),
		'--connect-timeout', '{}'.format(CONN_TIMEOUT),
		'--max-time', '{}'.format(CONN_TIMEOUT * 2),
		'{}/json'.format(MGMT_HOST)
	]

	# get the VPN server location, not the location of the device
	if DEVICE_TYPE in [3, 5]:
		try:
			shell_check_output_cmd('ip link | grep {}'.format(TUN_IFACE))
			cmd.append('--interface')
			cmd.append(TUN_IFACE)
		except:
			pass

	try:
		result = run_shell_cmd(cmd)
		if DEBUG: print('run_shell_cmd: {}'.format(result))
		assert result[0] == 0
		data = json.loads(result[1])
	except Exception as e:
		print('{}: family={} data={} e={}'.format(
			stack()[0][3],
			family,
			data,
			repr(e)
		))
	return data


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_ip_address(ifname):
	try:
		s = socket.socket(
			socket.AF_INET,
			socket.SOCK_DGRAM
		)
		ipaddr = socket.inet_ntoa(
			fcntl.ioctl(
				s.fileno(),
				0x8915,
				struct.pack('256s', ifname[:15].encode())
			)[20:24]
		)
	except:
		ipaddr = None
	return ipaddr


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_default_iface():
	route = '/proc/net/route'
	with open(route) as f:
		for line in f.readlines():
			try:
				iface, dest, _, flags, _, _, _, _, _, _, _, =  line.strip().split()
				if dest != '00000000' or not int(flags, 16) & 2:
					continue
				return iface
			except:
				continue


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_stations():
	stations = 0
	try:
		result = run_shell_cmd(
			[
				'/bin/bash',
				'{}/scripts/list-stations.sh'.format(WORKDIR)
			]
		)
		if result[0] == 0: stations = int(result[1].strip('\n'))
	except:
		pass
	return stations


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def resolve_dns(host='us.{}'.format(DNS_HOST), record='A', family=4):
	res = None
	try:
		resolver = dns.resolver.Resolver()
		resolver.nameservers=DNS_SERVERS
		if family == 6: resolver.nameservers=DNS6_SERVERS
		answers = dns.resolver.query(host, record)
		for rdata in answers:
			res = rdata.to_text() # always last record
		try:
			if family == 4:
				# fudge to make dns.resolver work with Nuitka compiled code
				pat = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
				if not pat.match(res):
					addr_long = int(res.split(' ')[2], 16)
					res = socket.inet_ntoa(struct.pack('>L', addr_long))
		except:
			pass
		return res
	except dns.resolver.NoAnswer:
		return None


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def run_speedtest():
	server = '{}.1'.format(
		'.'.join(
			get_ip_address(
				TUN_IFACE
			).split('.')[:-1]
		)
	)
	cmd = [
		'/usr/bin/iperf',
		'--client',
		server,
		'--nodelay',
		'--dualtest'
	]
	if DEBUG: print('{}: cmd={}'.format(stack()[0][3], cmd))
	p = run_shell_cmd_nowait(cmd)
	queue = Queue()
	thread = Thread(target=enqueue_output, args=(p.stdout, queue))
	thread.daemon = True
	thread.start()
	return queue, p


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def decode_jwt_payload(encoded=None):
	payload = dict()
	try:
		hdr = jwt.encode({}, '', algorithm='HS256').split('.')[0]
		sig = jwt.encode({}, '', algorithm='HS256').split('.')[2]
		payload = jwt.decode(
			'{}.{}.{}'.format(
				hdr,
				encoded,
				sig
			),
			options={'verify_signature': False},
			algorithms=['HS256']
		)
		if DEBUG: print(
			'{}: hdr={} sig={} payload={}'.format(
				stack()[0][3],
				hdr,
				sig,
				payload
			)
		)
	except Exception:
		if DEBUG: print_exc()
		payload = dict()

	try:
		payload['u'] = socket.inet_ntoa(
			struct.pack(
				'!L', int(payload['u'])
			)
		)
	except Exception:
		if DEBUG: print_exc()

	return payload


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def run_iotest(test=0):
	data_vol = shell_check_output_cmd(
		'mount | grep "%s" | head -n 1 | awk \'{print $1}\'' % DATADIR
	).strip('\n')
	cmd = [
		'hdparm'
	]
	if test == 0:
		cmd.append('-t')
	if test == 1:
		cmd.append('-T')
	cmd.append(data_vol)
	if test == 2:
		cmd = [
			'/bin/bash',
			'{}/scripts/dd-write-test.sh'.format(WORKDIR)
		]
	if DEBUG: print('{}: cmd={}'.format(stack()[0][3], cmd))
	p = run_shell_cmd_nowait(cmd)
	queue = Queue()
	thread = Thread(target=enqueue_output, args=(p.stdout, queue))
	thread.daemon = True
	thread.start()
	return queue, p


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_container_id():
	cmd = [
		'/usr/bin/dig',
		'+short',
		'-x',
		get_ip_address(get_default_iface())
	]
	try:
		result = run_shell_cmd(cmd)
		if DEBUG: print('run_shell_cmd: {}'.format(result))
		assert result[0] == 0
		assert result[1]
	except Exception as e:
		print('{}: e={}'.format(
			stack()[0][3],
			repr(e)
		))
	return result[1].strip('\n')


@retry(Exception, cdata='method={}'.format(stack()[0][3]))
def get_container_name():
	ipaddr = get_ip_address(get_default_iface())
	hosts = open('/etc/hosts').read().split('\n')
	host = [h for h in hosts if h.startswith(ipaddr)]
	try:
		container_name = host[0].split('\t')[1]
	except:
		container_name = 'localhost'
	return container_name
