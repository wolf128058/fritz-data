#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, line-too-long

import argparse
from getpass import getpass
import urllib3
from fritzconnection import FritzConnection
from fritzhosts import FritzHosts
from fritzstatus import FritzStatus

# So sorry for this one, but otherwise we will be fucked up by tons of warnings, because of self-signed certificates on your fritz-box
urllib3.disable_warnings()

ARG_PARSER = argparse.ArgumentParser(
    description='Get Data from your Fritz-Box')
ARG_PARSER.add_argument('-i', '--host', default='192.168.178.1', help=r'the hostname/ip of your fritzbox')
ARG_PARSER.add_argument('-p', '--password', default=None, help=r'the password of your fritzbox')
ARGS = ARG_PARSER.parse_args()

if ARGS.password is None:
    ARGS.password = getpass('Your Fritzbox-Password:')

METRICS = {}
INFO = {}
F_CONN = FritzConnection(address=ARGS.host, password=ARGS.password)
F_HOSTS = FritzHosts(F_CONN)
F_STATUS = FritzStatus(F_CONN)

MY_HOSTS = F_HOSTS.get_hosts_info()
ACTIVE_HOSTS = []
for host in MY_HOSTS:
    if int(host['status']) == 1:
        ACTIVE_HOSTS.append(host)
METRICS['ACTIVE_HOSTS'] = len(ACTIVE_HOSTS)

METRICS['linked'] = 0
if F_STATUS.is_linked:
    METRICS['linked'] = 1

METRICS['connected'] = 0
if F_STATUS.is_connected:
    METRICS['connected'] = 1

METRICS['uptime_s'] = F_STATUS.uptime
METRICS['wan_tx_bytes'] = F_STATUS.bytes_sent
METRICS['wan_rx_bytes'] = F_STATUS.bytes_received
METRICS['wan_maxup_byteps'] = F_STATUS.max_byte_rate[0]
METRICS['wan_maxdown_byteps'] = F_STATUS.max_byte_rate[1]

INFO['external_ip'] = F_STATUS.external_ip
INFO['model'] = F_STATUS.modelname


print(METRICS)
print(INFO)
