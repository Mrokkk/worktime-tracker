#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import argparse
import datetime

DB_FILE = os.path.expanduser('~') + '/.worktime'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=int, help='Log worktime')
    parser.add_argument('-u', '--uptime', help='Log worktime from current uptime', action='store_true')
    parser.add_argument('-s', '--summary', help='Show log summary', action='store_true')
    parser.add_argument('-l', '--log', help='Show log', action='store_true')
    return parser.parse_args()

def show_summary(data):
    full_worktime, delta = 0, 0
    size = len(data['data'])
    for entry in data['data']:
        entry_value = float(entry['worktime'])
        full_worktime += entry_value
        delta += entry_value - 8
    print('Per day: ' + "{0:.2f}".format(full_worktime / size) + ' h')
    print('Delta: ' + "{0:.2f}".format(delta) + ' h')

def show_log(data):
    full_worktime = 0
    size = len(data['data'])
    for entry in data['data']:
        full_worktime += float(entry['worktime'])
        print(datetime.datetime.fromtimestamp(float(entry['timestamp'])
            ).strftime('%Y-%m-%d %H:%M:%S') + ' : logged ' + entry['worktime'] + ' h')
    print('Full worktime: ' + "{0:.2f}".format(full_worktime) + ' h')
    print('Per day: ' + "{0:.2f}".format(full_worktime / size) + ' h')

def read_db():
    with open(DB_FILE, 'r') as db_file:
        return json.load(db_file)

def read_uptime():
    with open('/proc/uptime', 'r') as f:
        return float(f.readline().split()[0]) / 3600

def add_worktime(data, worktime):
    data["data"].append({'worktime': "{0:.2f}".format(round(worktime, 2)), 'timestamp': str(time.time())})
    with open(DB_FILE, 'w+') as db_file:
        json.dump(data, db_file)

def main():
    os.umask(0o077)
    args = parse_args()
    worktime = read_uptime() if args.uptime else args.time
    data = read_db() if os.path.exists(DB_FILE) else {"data": []}
    if (args.log):
        show_log(data)
    elif (args.summary):
        show_summary(data)
    else:
        add_worktime(data, worktime)

if __name__ == "__main__":
    main()
