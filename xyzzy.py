#!/usr/bin/env python

#
# xyzzy.py
# Copyright (C) 2017 Alexei Frolov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import argparse, os, sys
from stat import *

from xyzzy.pwgen import pwgen
from xyzzy.matrix_bot import MatrixBot

PROGRAM_NAME = 'xyzzy'
CONFIG_FILE = '%src' % PROGRAM_NAME


def setup(prog, config_path):
    path = config_path if config_path else './.%s' % CONFIG_FILE
    try:
        os.stat(path)
        print("Warning: `%s' already exists and will be overwritten" % path)
        if input('Continue? [y/n] ').lower() != 'y':
            return 0
    except EOFError:
        print('')
        return 0
    except FileNotFoundError:
        pass

    print('Creating a new Matrix account for %s' % PROGRAM_NAME)
    try:
        username = input('Enter a username: ')
    except EOFError:
        print('')
        return 0

    if not username:
        print('%s: invalid username provided' % prog, file=sys.stderr)
        return 1

    password = pwgen()

    if not password:
        print('%s: could not generate password' % prog, file=sys.stderr)
        return 1

    xyzzy = MatrixBot(username)
    try:
        xyzzy.register(password)
    except MatrixBot.RegistrationError:
        print('%s: failed to register Matrix account' % prog, file=sys.stderr)

    try:
        f = open(path, 'w')
        f.write('user=%s\n' % username)
        f.write('pass=%s\n' % password)
        f.close()
    except IOError as e:
        print('%s: %s' % (path, e.strerror), file=sys.stderr)
        return 1

    print('Settings saved to %s' % path)
    return 0


def get_settings(path):
    config_keys = ['user', 'pass', 'rooms']
    settings = {}

    for k in config_keys:
        settings[k] = None

    try:
        f = open(path, 'r')
    except IOError as e:
        print('%s: %s' % (path, e.strerror), file=sys.stderr)
        return None

    for lineno, line in enumerate(f, 1):
        tokens = line.strip().split('=', 1)

        if len(tokens) != 2:
            print('%s:%d: invalid syntax' % (path, lineno), file=sys.stderr)
            continue
        if tokens[0] not in settings:
            print("%s:%d: invalid key `%s'" % (path, lineno, tokens[0]),
                  file=sys.stderr)
            continue

        if tokens[0] == 'rooms':
            settings[tokens[0]] = tokens[1].split(',')
        else:
            settings[tokens[0]] = tokens[1]

    f.close()
    return settings


def read_config(prog, config_path):
    found_config = False
    paths = []

    if config_path:
        try:
            stat = os.stat(config_path)
            if S_ISREG(stat.st_mode):
                path = config_path
            else:
                print('%s: not a regular file' % config_path, file=sys.stderr)
                return None
        except FileNotFoundError as e:
            print('%s: %s' % (config_path, e.strerror), file=sys.stderr)
            return None
    else:
        paths.append('./.%s' % CONFIG_FILE)
        if 'XDG_CONFIG_HOME' in os.environ:
            paths.append('%s/%s' % (os.environ['XDG_CONFIG_HOME'], CONFIG_FILE))
        paths.append('%s/.%s' % (os.environ['HOME'], CONFIG_FILE))
        paths.append('/etc/%s' % CONFIG_FILE)

        for path in paths:
            try:
                stat = os.stat(path)
                if S_ISREG(stat.st_mode):
                    found_config = True
                    break
                else:
                    print('%s: not a regular file' % path, file=sys.stderr)
            except FileNotFoundError:
                continue

        if not found_config:
            print('%s: could not find configuration file' % prog,
                  file=sys.stderr)
            print("Run `%s --setup' to create a new config" % prog,
                  file=sys.stderr)
            return None

    return get_settings(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Matrix chat bot')
    parser.add_argument('-f', '--file', type=str,
                        help='use FILE as the config file')
    parser.add_argument('--setup', action='store_true',
                        help='create a new Matrix account for the bot')

    args = parser.parse_args()

    if args.setup:
        exit(setup(sys.argv[0], args.file))

    settings = read_config(sys.argv[0], args.file)
    if settings is None:
        exit(1)

    rooms = settings['rooms'] or []

    xyzzy = MatrixBot(settings['user'])
    try:
        xyzzy.login(settings['pass'])
        for room in rooms:
            try:
                xyzzy.join_room(room)
            except MatrixBot.RoomError as e:
                print('%s: %s: %s' % (sys.argv[0], room, e), file=sys.stderr)
    except MatrixBot.InvalidLoginError:
        print('%s: invalid username or password' % sys.argv[0], file=sys.stderr)
        exit(1)

    xyzzy.listen()
