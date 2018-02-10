#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import argparse
import datetime

DB_FILE = os.path.expanduser('~') + '/.worktime'
REQUIRED_WORKTIME_PER_DAY = 8.0

def convert_minutes(time):
    hours, minutes = int(abs(time) / 60), int(abs(time) % 60)
    return '{}{:02d}h{:02d}'.format('-' if time < 0 else '', hours, minutes)

def print_summary(full_worktime, days_of_work, delta):
    print('Summary:')
    print('  days of work:', days_of_work)
    print('  worktime per day:', '{}'.format(convert_minutes(full_worktime / days_of_work)))
    print('  worktime delta:', '{}'.format(convert_minutes(delta)))

def print_entry(timestamp, worktime):
    print(timestamp.strftime('%Y-%m-%d %H:%M:%S'), ': logged', convert_minutes(worktime))

def show_log(data, show_pre_entry=True):
    full_worktime, delta = 0, 0
    for days_of_work, entry in enumerate(data['data'], start=1):
        date = datetime.datetime.fromtimestamp(float(entry['timestamp']))
        entry_value = entry['worktime']
        full_worktime += entry_value
        delta += entry_value - REQUIRED_WORKTIME_PER_DAY * 60
        if show_pre_entry:
            print_entry(date, entry_value)
    print_summary(full_worktime, days_of_work, delta)

def show(args):
    data = read_db() if os.path.exists(DB_FILE) else {'data': []}
    show_log(data, args.full)

def read_db():
    with open(DB_FILE, 'r') as db_file:
        return json.load(db_file)

def read_uptime():
    with open('/proc/uptime', 'r') as f:
        return float(f.readline().split()[0]) / 60

def last_entry_has_the_same_day(data, current_day):
    try:
        last_day = data['data'][-1]['day']
        if current_day == last_day:
            return True
    except:
        return False

def add_worktime(data, worktime):
    current_day = time.strftime('%x')
    current_timestamp = str(time.time())
    if last_entry_has_the_same_day(data, current_day):
        data['data'][-1]['worktime'] += worktime
        data['data'][-1]['timestamp'] = current_timestamp
    else:
        data['data'].append({'worktime': worktime, 'timestamp': current_timestamp, 'day': current_day})
    with open(DB_FILE, 'w+') as db_file:
        json.dump(data, db_file)

def add(args):
    if not args.time and not args.uptime:
        print('No worktime given')
        return
    if args.time:
        splitted = args.time.split('h')
        time = int(splitted[0]) * 60 + int(splitted[1])
    worktime = read_uptime() if args.uptime else time
    data = read_db() if os.path.exists(DB_FILE) else {"data": []}
    add_worktime(data, worktime)

def add_show_command(subparsers):
    parser_show = subparsers.add_parser('show')
    parser_show.add_argument('-f', '--full', help='Show full log', action='store_true')
    parser_show.set_defaults(func=show)

def add_add_command(subparsers):
    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('time', nargs='?', type=str, help='Worktime in hours (format HhM)')
    parser_add.add_argument('-u', '--uptime', action='store_true', help='Log worktime from current uptime')
    parser_add.set_defaults(func=add)

def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='subcommand help')
    add_show_command(subparsers)
    add_add_command(subparsers)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

