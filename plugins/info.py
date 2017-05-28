#
# plugins/info.py
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

from xyzzy.plugin import Plugin

class InfoPlugin(Plugin):
    PLUGIN_COMMAND = 'info'
    GITHUB_REPO = 'https://github.com/frolv/xyzzy'

    def run(self, argv):
        if len(argv) == 1:
            response = 'xyzzy matrix bot'
        elif argv[1] == 'source':
            response = InfoPlugin.GITHUB_REPO
        else:
            response = ''

        return {
            'type': 'text',
            'content': response
        }
