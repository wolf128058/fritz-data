#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, line-too-long

import sys
import argparse
from getpass import getpass
from time import sleep
import datetime
from fritzconnection import FritzConnection

def is_connected(fritz_connection):
    """
    Returns True if the FritzBox has established an internet-connection.
    """
    status = fritz_connection.call_action('WANIPConnection', 'GetStatusInfo')
    return status['NewConnectionStatus'] == 'Connected'

def reconnect(fritz_connection):
    """Makes a reconnection with a new external ip."""
    fritz_connection.reconnect()

def reconnect_loop(wait_seconds, fritz_connection):
    print('trying to reconnect...')
    reconnect(fritz_connection)
    print('meanwhile...')
    if is_connected(fritz_connection):
        print('reconnection successful.')
    else:
        print(datetime.datetime.now().isoformat() +  ' >> reconnection failed.')
        sleep(wait_seconds)
        reconnect_loop(wait_seconds, fritz_connection)

ARG_PARSER = argparse.ArgumentParser(
    description='Get Data from your Fritz-Box')
ARG_PARSER.add_argument('-i', '--host', default='192.168.178.1', help=r'the hostname/ip of your fritzbox')
ARG_PARSER.add_argument('-p', '--password', default=None, help=r'the password of your fritzbox')
ARGS = ARG_PARSER.parse_args()

if ARGS.password is None:
    ARGS.password = getpass('Your Fritzbox-Password:')

F_CONN = FritzConnection(address=ARGS.host, password=ARGS.password, use_tls=True)

if is_connected(F_CONN):
    print('Okay. Internet is up!')
    sys.exit(0)
else:
    reconnect_loop(300, F_CONN)
