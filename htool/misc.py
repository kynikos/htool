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

from .dom import _Element, _ElementContainer
from .text import _Text, TextRaw


class Doctype(_Element):
    BREAK_BEFORE = True
    BREAK_AFTER = True

    def compile(self, indent=""):
        return '<!doctype html>'


class Comment(_Element):
    # TODO: Does text have to be escaped in comments?
    # TODO: Document that the text isn't escaped in this case
    DEFAULT_ESCAPE_TEXT = TextRaw

    def __init__(self, *text):
        super(Comment, self).__init__()
        self.text = ''
        for textbit in text:
            if not isinstance(textbit, _Text):
                textbit = self.DefaultContentEscape(textbit)
            self.text = ''.join((self.text, textbit.escaped))

    def compile(self, indent=""):
        # TODO: Optionally surround text with spaces?
        return self.text.join(('<!--', '-->'))


class ElementContainer(_ElementContainer):
    """
    Safe alias for the "private" _ElementContainer class.
    """
    pass


class _File(_Element):
    BREAK_BEFORE = True
    BREAK_AFTER = True

    def __init__(self, filename):
        super(_File, self).__init__()
        with open(filename, 'r') as f:
            self.text = self.DefaultContentEscape(f.read())

    def compile(self, indent=""):
        return self.text.escaped


class TextFile(_File):
    pass


class HTMLFile(_File):
    DEFAULT_ESCAPE_TEXT = TextRaw
