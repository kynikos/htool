# Htool - HyperText Object-Oriented Layer.
# Copyright (C) 2016 Dario Giovannetti <dev@dariogiovannetti.net>
#
# This file is part of Htool.
#
# Htool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Htool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Htool.  If not, see <http://www.gnu.org/licenses/>.

# The module must also support Python 2
# http://python-future.org/
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# Support Python 2.6
# from builtins import *

try:
    from html import escape as html_escape
except ImportError:
    # Old Python versions don't have html.escape()
    from cgi import escape as _html_escape
    html_escape = lambda text: _html_escape(text, quote=True)  # NOQA


class _Text(object):
    def __init__(self, rawtext):
        self.raw = rawtext


class TextRaw(_Text):
    def __init__(self, rawtext):
        super(TextRaw, self).__init__(rawtext)
        self.escaped = rawtext


class TextEscaped(_Text):
    # TODO: Make another smarter class that leaves already-escaped text as
    #       is, e.g. named character references (e.g. '&gt;')
    #       Probably use the html.entities.html5 dictionary
    def __init__(self, rawtext):
        super(TextEscaped, self).__init__(rawtext)
        try:
            # It's important to first html_escape, then encode, not vice versa
            escaped = html_escape(rawtext).encode('ascii', 'xmlcharrefreplace')
        except AttributeError:
            self.escaped = str(rawtext)
        else:
            # Finally decode, otherwise 'escaped' is a bytes object
            self.escaped = escaped.decode('utf-8')
