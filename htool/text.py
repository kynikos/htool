# lib.py.htool - Check the status of code repositories under a root directory.
# Copyright (C) 2016 Dario Giovannetti <dev@dariogiovannetti.net>
#
# This file is part of lib.py.htool.
#
# lib.py.htool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lib.py.htool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lib.py.htool.  If not, see <http://www.gnu.org/licenses/>.

# The module must also support Python 2
# http://python-future.org/
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import html


class _Text(object):
    def __init__(self, rawtext):
        self.raw = rawtext


class TextRaw(_Text):
    def __init__(self, rawtext):
        super().__init__(rawtext)
        self.escaped = rawtext


class TextEscaped(_Text):
    # TODO: Make another smarter class that leaves already-escaped text as
    #       is, e.g. named character references (e.g. '&gt;')
    #       Probably use the html.entities.html5 dictionary
    def __init__(self, rawtext):
        super().__init__(rawtext)
        self.escaped = html.escape(str(rawtext))
