#
# xyzzy/matrix_bot.py
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

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError

from markdown import markdown
from time import time

from . import plugin
from . import arguments
from plugins.info import InfoPlugin
from plugins.interject import InterjectPlugin
from plugins.sed import SedPlugin

DEFAULT_MATRIX_SERVER = 'https://matrix.org'

class MatrixBot:
    COMMAND_PREFIX = ','
    ACTIVE_BOT_PLUGINS = [
        InfoPlugin,
        InterjectPlugin
    ]
    PASSIVE_BOT_PLUGINS = [
        SedPlugin
    ]

    def __init__(self, username):
        self.username = username
        self.client = MatrixClient(DEFAULT_MATRIX_SERVER)
        self.active_plugins = {}
        self.passive_plugins = []

        for plugin in MatrixBot.ACTIVE_BOT_PLUGINS:
            self.active_plugins[plugin.PLUGIN_COMMAND] = plugin()

        for plugin in MatrixBot.PASSIVE_BOT_PLUGINS:
            self.passive_plugins.append(plugin())


    def register(self, password):
        """ Register a new Matrix account """

        try:
            # register_with_password is broken in the current
            # version of matrix-python-sdk, so this will 401.
            self.client.register_with_password(username=self.username,
                                               password=password)
        except MatrixRequestError as e:
            raise MatrixBot.RegistrationError()


    def login(self, password):
        """ Login to Matrix server """

        try:
            self.client.login_with_password(username=self.username,
                                            password=password)
        except MatrixRequestError as e:
            if e.code == 403:
                raise MatrixBot.InvalidLoginError()


    def join_room(self, room):
        """ Join a Matrix room """

        room = '#%s:matrix.org' % room
        try:
            r = self.client.join_room(room)
        except MatrixRequestError as e:
            if e.code == 400:
                raise MatrixBot.RoomError('invalid Matrix room format')
            else:
                raise MatrixBot.RoomError('could not find room')

        r.add_listener(self.event_listener)


    def listen(self):
        self.client.start_listener_thread()
        while True:
            try:
                input('')
            except EOFError:
                break

    def handle_response(self, response, room):
        if response:
            if not response['content']:
                return
            if response['type'] == 'text':
                room.send_text(response['content'])
            elif response['type'] == 'markdown':
                html = markdown(response['content'],
                        extensions=['markdown.extensions.fenced_code'])
                room.send_html(html, response['content'])

    def event_listener(self, room, event):
        """ Matrix event callback """

        print(event)
        if event['type'] == 'm.room.message':
            if event['content']['msgtype'] == 'm.text':
                msg = event['content']['body']
                if not msg:
                    return

                has_prefix = msg[0] == MatrixBot.COMMAND_PREFIX

                if has_prefix:
                    trimmed_message = msg[1:]
                else:
                    trimmed_message = msg

                try:
                    args = arguments.Arguments(trimmed_message, room, event, self)
                except MatrixBot.UnterminatedQuoteError:
                    room.send_text('error: unterminated quote')
                    return

                if not args:
                    return

                if has_prefix and args.argv[0] in self.active_plugins:
                    self.handle_response(
                            self.active_plugins[args.argv[0]].run(args), room)
                else:
                    for plug in self.passive_plugins:
                        status, response = plug.accept(args)
                        self.handle_response(response, room)
                        if status:
                            return

    def redact_message(self, event, room):
        path = '/rooms/%s/redact/%s/%s' % (
                room.room_id,
                event['event_id'],
                str(room.client.api.txn_id) + str(int(time()) * 1000)
        )

        content = { 'reason': 'Sed correction' }
        room.client.api._send('PUT', path, content, {}, {})

    class RegistrationError(Exception):
        pass

    class InvalidLoginError(Exception):
        pass

    class RoomError(Exception):
        pass

    class UnterminatedQuoteError(Exception):
        pass
