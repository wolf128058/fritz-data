#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, line-too-long

import sys
import argparse
import json
from getpass import getpass
from fritzconnection import FritzConnection
from fritzstatus import FritzStatus

FRITZINFO = {}


def get_hosts_info(fritz_connection):
    """
    Returns a list of dicts with information about the known hosts.
    The dict-keys are: 'ip', 'name', 'mac', 'status'
    """
    result = []
    index = 0
    while index < int(fritz_connection.call_action(service_name='Hosts1', action_name='GetHostNumberOfEntries')['NewHostNumberOfEntries']):
        host = fritz_connection.call_action(
            service_name='Hosts1', action_name='GetGenericHostEntry', NewIndex=index)
        result.append({
            'ip': host['NewIPAddress'],
            'name': host['NewHostName'],
            'mac': host['NewMACAddress'],
            'status': host['NewActive']})
        index += 1
    return result


ARG_PARSER = argparse.ArgumentParser(
    description='Get Data from your Fritz-Box')
ARG_PARSER.add_argument('-i', '--host', default='192.168.178.1',
                        help=r'the hostname/ip of your fritzbox')
ARG_PARSER.add_argument('-p', '--password', default=None,
                        help=r'the password of your fritzbox')
ARG_PARSER.add_argument('-n', '--numeric', action='store_true',
                        help=r'filter: show only numeric information')
ARGS = ARG_PARSER.parse_args()

if ARGS.password is None:
    ARGS.password = getpass('Your Fritzbox-Password:')

try:
    F_CONN = FritzConnection(
        address=ARGS.host, password=ARGS.password, use_tls=True)
except OSError:
    sys.exit('Could not connect to Fritzbox. I quit.')

F_STATUS = FritzStatus(F_CONN)

if not ARGS.numeric:
    FRITZINFO['model'] = F_CONN.modelname
    FRITZINFO['system_version'] = F_CONN.device_manager.system_version
    FRITZINFO['linked'] = F_STATUS.is_linked
    FRITZINFO['connected'] = F_STATUS.is_connected
    FRITZINFO['external_ip'] = F_STATUS.external_ip
else:
    FRITZINFO['linked'] = 0
    if F_STATUS.is_linked:
        FRITZINFO['linked'] = 1

    FRITZINFO['connected'] = 0
    if F_STATUS.is_connected:
        FRITZINFO['connected'] = 1

FRITZINFO['uptime'] = F_STATUS.uptime
FRITZINFO['rx_bytes'] = F_STATUS.bytes_received
FRITZINFO['tx_bytes'] = F_STATUS.bytes_sent
FRITZINFO['max_bitrate_up'] = F_STATUS.max_bit_rate[0]
FRITZINFO['max_bitrate_down'] = F_STATUS.max_bit_rate[1]

if not ARGS.numeric:
    FRITZINFO['hosts'] = get_hosts_info(F_CONN)
else:
    COUNT_HOSTS = 0
    for single_host in get_hosts_info(F_CONN):
        if single_host['status']:
            COUNT_HOSTS += 1
    FRITZINFO['hosts'] = COUNT_HOSTS

JSON_OBJECT = json.dumps(FRITZINFO, indent=4)
print(JSON_OBJECT)
