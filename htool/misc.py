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

from .dom import _Node, _Element, _ElementContainer
from .text import _Text, TextRaw


class Doctype(_Node):
    # Not an HTML tag, but can be expected to be in this module
    def compile(self):
        return '<!doctype html>'


class Comment(_Element):
    # Not an HTML tag, but can be expected to be in this module
    # TODO: Does text have to be escaped in comments?
    # TODO: Document that the text isn't escaped in this case
    DEFAULT_ESCAPE_TEXT = TextRaw

    def __init__(self, *text):
        super().__init__()
        self.text = ''
        for textbit in text:
            if not isinstance(textbit, _Text):
                textbit = self.DefaultContentEscape(textbit)
            self.text = ''.join((self.text, textbit.escaped))

    def compile(self):
        # TODO: Optionally surround text with spaces?
        return self.text.join(('<!--', '-->'))


class ElementContainer(_ElementContainer):
    """
    Safe alias for the "private" _ElementContainer class.
    """
    # Not an HTML tag, but can be expected to be in this module
    pass
