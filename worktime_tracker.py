#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import argparse
import datetime

DB_FILE = os.path.expanduser('~') + '/.worktime'
REQUIRED_WORKTIME_PER_DAY = 8.0

def print_summary(full_worktime, days_of_work, delta):
    print('Summary:')
    print('  days of work:', days_of_work)
    print('  worktime per day:', '{0:.2f}'.format(full_worktime / days_of_work), 'h')
    print('  worktime delta:', '{0:.2f}'.format(delta), 'h')

def print_entry(timestamp, worktime):
    print(timestamp.strftime('%Y-%m-%d %H:%M:%S'), ': logged', worktime, 'h')

def show_log(data, show_pre_entry=True):
    full_worktime, days_of_work, delta = 0, 0, 0
    last_entry = None
    last_timestamp = 0.0
    for entry in data['data']:
        timestamp = float(entry['timestamp'])
        date = datetime.datetime.fromtimestamp(timestamp)
        entry_value = float(entry['worktime'])
        full_worktime += entry_value
        old = datetime.datetime.fromtimestamp(last_timestamp)
        diff = datetime.timedelta(days=date.day) - datetime.timedelta(days=old.day)
        if diff.days:
            days_of_work += 1
            delta += entry_value - REQUIRED_WORKTIME_PER_DAY
        else:
            delta += entry_value
        if (show_pre_entry):
            print_entry(date, entry_value)
        last_timestamp = timestamp
    print_summary(full_worktime, days_of_work, delta)

def show(args):
    data = read_db() if os.path.exists(DB_FILE) else {"data": []}
    show_log(data, args.full)

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

def add(args):
    if not args.time and not args.uptime:
        print('No worktime given')
        return
    worktime = read_uptime() if args.uptime else args.time
    data = read_db() if os.path.exists(DB_FILE) else {"data": []}
    add_worktime(data, worktime)

def add_show_command(subparsers):
    parser_show = subparsers.add_parser('show')
    parser_show.add_argument('-f', '--full', help='Show full log', action='store_true')
    parser_show.set_defaults(func=show)

def add_add_command(subparsers):
    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('time', nargs='?', type=float, default=0.0, help='Worktime in hours')
    parser_add.add_argument('-u', '--uptime', action='store_true', help='Log worktime from current uptime')
    parser_add.set_defaults(func=add)

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='subcommand help')
    add_show_command(subparsers)
    add_add_command(subparsers)
    args = parser.parse_args()
    args.func(args)

def main():
    os.umask(0o077)
    parse_args()

if __name__ == "__main__":
    main()
