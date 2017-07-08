#
# xyzzy/plugin.py
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

class Plugin:
    """ Command which calls the plugin """
    PLUGIN_COMMAND = ''

    def run(self, arguments):
        """
        Main plugin function called when a command is received
        Returns a response dictionary containing two fields:
            'type': content type - either 'text' or 'markdown'
            'content': the message to send as a response
        """
        pass

    def accept(self, arguments):
        """
        For passive plugins to choose if they want the message to
        be processed by other commands.
        Returns (status, response) status is true no other plugins
        should be consulted otherwise continue asking plugins.
        Response the same an in self.run
        """
        return False, None

