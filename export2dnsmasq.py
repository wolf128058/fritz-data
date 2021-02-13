#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, line-too-long

import argparse
from getpass import getpass
import urllib3
from fritzconnection import FritzConnection

def get_hosts_info(fritz_connection):
    """
    Returns a list of dicts with information about the known hosts.
    The dict-keys are: 'ip', 'name', 'mac', 'status'
    """
    result = []
    index = 0
    while index < int(fritz_connection.call_action(service_name='Hosts1', action_name='GetHostNumberOfEntries')['NewHostNumberOfEntries']):
        host = fritz_connection.call_action(service_name='Hosts1', action_name='GetGenericHostEntry', NewIndex=index)
        result.append({
            'ip': host['NewIPAddress'],
            'name': host['NewHostName'],
            'mac': host['NewMACAddress'],
            'status': host['NewActive']})
        index += 1
    return result

ARG_PARSER = argparse.ArgumentParser(
    description='Get Data from your Fritz-Box')
ARG_PARSER.add_argument('-i', '--host', default='192.168.178.1', help=r'the hostname/ip of your fritzbox')
ARG_PARSER.add_argument('-p', '--password', default=None, help=r'the password of your fritzbox')
ARG_PARSER.add_argument('-f', '--file', default='tmpfile4dnsmasq.conf', help=r'path to export-file')
ARG_PARSER.add_argument('-s', '--suffix', default='.fritz.local', help=r'domain-suffix')
ARG_PARSER.add_argument('-a', '--filteractive', action='store_true', help=r'filter: only active entries')
ARGS = ARG_PARSER.parse_args()

if ARGS.password is None:
    ARGS.password = getpass('Your Fritzbox-Password:')

try:
    F_CONN = FritzConnection(address=ARGS.host, password=ARGS.password, use_tls=True)
except OSError:
    print('Could not connect to Fritzbox. I quit.')
    exit()

MY_HOSTS = get_hosts_info(F_CONN)
 
f = open(ARGS.file, "w")

yet_set = []

for host in MY_HOSTS:
    if 'ip' in host and 'name' in host and host['ip'] and host['name'] and str.lower(host['name']) not in yet_set:
        if ARGS.filteractive is not None and 'status' in host and not host['status']:
            continue
        host['name'] = str.lower(host['name'])
        f.write("address=/" + host['name'] + ARGS.suffix + "/" + host['ip'] + "\n")
        yet_set.append(host['name'])
f.close()
