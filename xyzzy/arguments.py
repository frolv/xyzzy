#
# xyzzy/arguments.py
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

class Arguments:
    raw = ''
    argv = []

    def __init__(self, raw_input, room=None, event=None, matrix_bot=None):
        self.raw = raw_input
        self.argv = self.split_string(raw_input)
        self.room = room
        self.current_event = event
        self.matrix_bot = matrix_bot

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

