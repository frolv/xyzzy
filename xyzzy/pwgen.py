#
# xyzzy/pwgen.py
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

import subprocess, shutil, sys

DEFAULT_PASSWORD_LENGTH = 32

def pwgen():
    pwgen_path = shutil.which('pwgen')
    if not pwgen_path:
        return pwgen_insecure()

    argv = [pwgen_path, '-ncsy', str(DEFAULT_PASSWORD_LENGTH), '1']
    try:
        password = subprocess.check_output(argv).rstrip().decode()
    except subprocess.CalledProcessError:
        password = None

    return password

def pwgen_insecure():
    # TODO: use some other algorithm
    print("You do not have `pwgen' installed. Cannot generate password.",
          file=sys.stderr)
    exit(1)
