#
# plugins/sed.py
# Copyright (C) 2017 Josh Wolfe
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
import re

class SedPlugin(Plugin):
    PLUGIN_COMMAND = 'sed'
    _groups = ()

    def run(self, arguments):
        flag = False
        for event in reversed(arguments.room.get_events()):
            if event['sender'] == arguments.current_event['sender']:
                if flag:
                    arguments.matrix_bot.redact_message(event, arguments.room)
                    return {
                        'type': 'markdown',
                        'content': '**%s**: %s' % (
                            arguments.current_event['sender'].split(':')[0][1:],
                            self.parse_sed(arguments, event)
                        )
                    }
                else:
                    flag = True

        return {
            'type': 'text',
            'content': ''
        }

    def accept(self, arguments):
        result = re.match(r'^s(\/|;|\||#| )([^\1]*)\1([^\1]*)\1([a-zA-Z]?)$',
                          arguments.raw)
        if not result:
            return False, None
        else:
            self._groups = result.groups()
            return True, self.run(arguments)

    def parse_sed(self, arguments, replace_event):
        return re.sub(self._groups[1], self._groups[2],
                      replace_event['content']['body'], 
                      0 if self._groups[3] == 'g' else 1)


