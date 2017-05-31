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

from . import plugin
from plugins.info import InfoPlugin
from plugins.interject import InterjectPlugin

DEFAULT_MATRIX_SERVER = 'https://matrix.org'

class MatrixBot:
    COMMAND_PREFIX = ','
    BOT_PLUGINS = [
        InfoPlugin,
        InterjectPlugin
    ]

    def __init__(self, username):
        self.username = username
        self.client = MatrixClient(DEFAULT_MATRIX_SERVER)
        self.plugins = {}

        for plugin in MatrixBot.BOT_PLUGINS:
            self.plugins[plugin.PLUGIN_COMMAND] = plugin()


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

    def event_listener(self, room, event):
        """ Matrix event callback """

        print(event)
        if event['type'] == 'm.room.message':
            if event['content']['msgtype'] == 'm.text':
                msg = event['content']['body']
                if msg[0] != MatrixBot.COMMAND_PREFIX:
                    return

                try:
                    argv = self.split_string(msg[1:])
                except MatrixBot.UnterminatedQuoteError:
                    room.send_text('error: unterminated quote')
                    return

                if not argv:
                    return

                if argv[0] in self.plugins:
                    response = self.plugins[argv[0]].run(argv)
                    if not response['content']:
                        return
                    if response['type'] == 'text':
                        room.send_text(response['content'])
                    elif response['type'] == 'markdown':
                        html = markdown(response['content'],
                                        extensions=['markdown.extensions.fenced_code'])
                        room.send_html(html, response['content'])


    def split_string(self, s):
        argv = []
        argc = 0
        i = 0

        arg = []
        while i < len(s):
            if s[i] == "'" or s[i] == '"' or s[i] == '`':
                i += self.read_quoted(s, arg, i)
                # print('after read quoted s[i] = "%s"' % s[i])
            elif s[i] == '\\':
                arg.append(s[i + 1] if i + 1 < len(s) else s[i])
                i += 2
            elif s[i] == ' ' or s[i] == '\t':
                argv.append(''.join(arg))
                arg.clear()
                i += 1
            else:
                arg.append(s[i])
                i += 1

        argv.append(''.join(arg))

        return argv


    def read_quoted(self, s, arg, i):
        quote = s[i]
        start = i
        i += 1

        if quote == '`':
            arg.append(quote)

        while i < len(s):
            if s[i] == quote:
                if quote == '`':
                    arg.append(quote)
                break
            elif s[i] == '\\':
                arg.append(s[i + 1] if i + 1 < len(s) else s[i])
                i += 2
            else:
                arg.append(s[i])
                i += 1

        if quote == '`':
            arg.append(quote)

        if i == len(s):
            raise MatrixBot.UnterminatedQuoteError()

        return i - start + 1


    class RegistrationError(Exception):
        pass

    class InvalidLoginError(Exception):
        pass

    class RoomError(Exception):
        pass

    class UnterminatedQuoteError(Exception):
        pass
