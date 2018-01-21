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

import itertools

from .dom import (_HTMLNewlineVoidElement, _HTMLNewlineElement,
                  _HTMLPrelineVoidElement, _HTMLPrelineElement,
                  _HTMLStartlineVoidElement, _HTMLStartlineElement,
                  _HTMLEndlineVoidElement, _HTMLEndlineElement,
                  _HTMLSamelineVoidElement, _HTMLSamelineElement)
from .text import TextRaw


class _List(_HTMLNewlineElement):
    # This class is too coupled with this module to be moved to a separate one
    def append_item(self, item):
        if not isinstance(item, Li):
            item = Li(item)
        self.append_child(item)

    def append_items(self, *items):
        for item in items:
            self.append_item(item)


class _Table(_HTMLNewlineElement):
    # This class is too coupled with this module to be moved to a separate one
    def append_header_row(self, *cells, **attributes):
        row = Tr(**attributes)
        self.append_child(row)
        row.append_header_cells(*cells)

    def append_data_row(self, *cells, **attributes):
        row = Tr(**attributes)
        self.append_child(row)
        row.append_data_cells(*cells)

    def append_header_rows(self, *rows, **attributes):
        for row in rows:
            self.append_header_row(*row, **attributes)

    def append_data_rows(self, *rows, **attributes):
        for row in rows:
            self.append_data_row(*row, **attributes)


class A(_HTMLSamelineElement):
    TAG = 'a'

    @classmethod
    def from_url(cls, url, **attributes):
        return cls(url, href=url, **attributes)


class Abbr(_HTMLSamelineElement):
    TAG = 'abbr'


class Address(_HTMLNewlineElement):
    TAG = 'address'


class Area(_HTMLNewlineVoidElement):
    TAG = 'area'


class Article(_HTMLNewlineElement):
    TAG = 'article'


class Aside(_HTMLNewlineElement):
    TAG = 'aside'


class Audio(_HTMLNewlineElement):
    TAG = 'audio'


class B(_HTMLSamelineElement):
    TAG = 'b'


class Base(_HTMLNewlineVoidElement):
    TAG = 'base'


class Bdi(_HTMLSamelineElement):
    TAG = 'bdi'


class Bdo(_HTMLSamelineElement):
    TAG = 'bdo'


class Blockquote(_HTMLNewlineElement):
    TAG = 'blockquote'


class Body(_HTMLNewlineElement):
    TAG = 'body'


class Br(_HTMLEndlineVoidElement):
    TAG = 'br'


class Button(_HTMLSamelineElement):
    TAG = 'button'


class Canvas(_HTMLSamelineElement):
    TAG = 'canvas'


class Caption(_HTMLNewlineElement):
    TAG = 'caption'


class Cite(_HTMLSamelineElement):
    TAG = 'cite'


class Code(_HTMLSamelineElement):
    TAG = 'code'


class Col(_HTMLNewlineVoidElement):
    TAG = 'col'


class Colgroup(_HTMLNewlineElement):
    TAG = 'colgroup'

    def populate(self, colN, classes=None):
        if classes:
            classes = itertools.cycle(classes)
            for x in range(colN):
                class_ = next(classes)
                self.append_child(Col(class_=class_))
        else:
            for x in range(colN):
                self.append_child(Col())
        # Return the object so that this method can be used directly when
        # instantiating Colgroup as an argument for a parent element
        return self


class Data(_HTMLSamelineElement):
    TAG = 'data'


class Datalist(_HTMLSamelineElement):
    TAG = 'datalist'


class Dd(_HTMLSamelineElement):
    TAG = 'dd'


class Del(_HTMLSamelineElement):
    TAG = 'del'


class Details(_HTMLNewlineElement):
    TAG = 'details'


class Dfn(_HTMLSamelineElement):
    TAG = 'dfn'


class Dialog(_HTMLNewlineElement):
    TAG = 'dialog'


class Div(_HTMLNewlineElement):
    TAG = 'div'


class Dl(_HTMLNewlineElement):
    TAG = 'dl'


class Dt(_HTMLSamelineElement):
    TAG = 'dt'


class Em(_HTMLSamelineElement):
    TAG = 'em'


class Embed(_HTMLNewlineVoidElement):
    TAG = 'embed'


class Fieldset(_HTMLNewlineElement):
    TAG = 'fieldset'


class Figcaption(_HTMLNewlineElement):
    TAG = 'figcaption'


class Figure(_HTMLNewlineElement):
    TAG = 'figure'


class Footer(_HTMLNewlineElement):
    TAG = 'footer'


class Form(_HTMLNewlineElement):
    TAG = 'form'


class H1(_HTMLNewlineElement):
    TAG = 'h1'


class H2(_HTMLNewlineElement):
    TAG = 'h2'


class H3(_HTMLNewlineElement):
    TAG = 'h3'


class H4(_HTMLNewlineElement):
    TAG = 'h4'


class H5(_HTMLNewlineElement):
    TAG = 'h5'


class H6(_HTMLNewlineElement):
    TAG = 'h6'


class Head(_HTMLNewlineElement):
    TAG = 'head'


class Header(_HTMLNewlineElement):
    TAG = 'header'


class Hgroup(_HTMLNewlineElement):
    TAG = 'hgroup'


class Hr(_HTMLNewlineVoidElement):
    TAG = 'hr'


class Html(_HTMLNewlineElement):
    TAG = 'html'


class I(_HTMLSamelineElement):
    TAG = 'i'


class Iframe(_HTMLNewlineElement):
    TAG = 'iframe'


class Img(_HTMLSamelineVoidElement):
    TAG = 'img'


class Input(_HTMLSamelineVoidElement):
    TAG = 'input'


class Ins(_HTMLSamelineElement):
    TAG = 'ins'


class Kbd(_HTMLSamelineElement):
    TAG = 'kbd'


class Label(_HTMLSamelineElement):
    TAG = 'label'


class Legend(_HTMLNewlineElement):
    TAG = 'legend'


class Li(_HTMLNewlineElement):
    TAG = 'li'


class Link(_HTMLNewlineVoidElement):
    TAG = 'link'

    @classmethod
    def css(cls, path, **attributes):
        return cls(href=path, type="text/css", rel="stylesheet", **attributes)

    @classmethod
    def favicon(cls, path, **attributes):
        return cls(href=path, rel="shortcut icon", **attributes)


class Main(_HTMLNewlineElement):
    TAG = 'main'


class Map(_HTMLNewlineElement):
    TAG = 'map'


class Mark(_HTMLSamelineElement):
    TAG = 'mark'


class Menu(_HTMLNewlineElement):
    TAG = 'menu'


class Menuitem(_HTMLNewlineElement):
    TAG = 'menuitem'


class Meta(_HTMLNewlineVoidElement):
    TAG = 'meta'


class Meter(_HTMLSamelineElement):
    TAG = 'meter'


class Nav(_HTMLNewlineElement):
    TAG = 'nav'


class Noscript(_HTMLNewlineElement):
    TAG = 'noscript'


class Object(_HTMLNewlineElement):
    TAG = 'object'


class Ol(_List):
    TAG = 'ol'


class Optgroup(_HTMLNewlineElement):
    TAG = 'optgroup'


class Option(_HTMLNewlineElement):
    TAG = 'option'


class Output(_HTMLSamelineElement):
    TAG = 'output'


class P(_HTMLNewlineElement):
    TAG = 'p'


class Param(_HTMLNewlineVoidElement):
    TAG = 'param'


class Picture(_HTMLNewlineElement):
    TAG = 'picture'


class Pre(_HTMLPrelineElement):
    TAG = 'pre'


class Progress(_HTMLSamelineElement):
    TAG = 'progress'


class Q(_HTMLSamelineElement):
    TAG = 'q'


class Rp(_HTMLSamelineElement):
    TAG = 'rp'


class Rt(_HTMLSamelineElement):
    TAG = 'rt'


class Rtc(_HTMLSamelineElement):
    TAG = 'rtc'


class Ruby(_HTMLNewlineElement):
    TAG = 'ruby'


class S(_HTMLSamelineElement):
    TAG = 's'


class Samp(_HTMLSamelineElement):
    TAG = 'samp'


class Script(_HTMLNewlineElement):
    TAG = 'script'
    # TODO: Document that the text isn't escaped in this case
    DEFAULT_ESCAPE_TEXT = TextRaw

    @classmethod
    def js(cls, *children, **attributes):
        return cls(*children, type='text/javascript', **attributes)


class Section(_HTMLNewlineElement):
    TAG = 'section'


class Select(_HTMLSamelineElement):
    TAG = 'select'


class Small(_HTMLSamelineElement):
    TAG = 'small'


class Source(_HTMLNewlineVoidElement):
    TAG = 'source'


class Span(_HTMLSamelineElement):
    TAG = 'span'


class Strong(_HTMLSamelineElement):
    TAG = 'strong'


class Style(_HTMLNewlineElement):
    TAG = 'style'


class Sub(_HTMLSamelineElement):
    TAG = 'sub'


class Summary(_HTMLNewlineElement):
    TAG = 'summary'


class Sup(_HTMLSamelineElement):
    TAG = 'sup'


class Table(_Table):
    TAG = 'table'


class Tbody(_Table):
    TAG = 'tbody'


class Td(_HTMLNewlineElement):
    TAG = 'td'


class Template(_HTMLNewlineElement):
    TAG = 'template'


class Textarea(_HTMLPrelineElement):
    TAG = 'textarea'


class Tfoot(_Table):
    TAG = 'tfoot'


class Th(_HTMLNewlineElement):
    TAG = 'th'


class Thead(_Table):
    TAG = 'thead'


class Time(_HTMLSamelineElement):
    TAG = 'time'


class Title(_HTMLNewlineElement):
    TAG = 'title'


class Tr(_HTMLNewlineElement):
    TAG = 'tr'

    def append_header_cell(self, cell):
        if not isinstance(cell, Th):
            cell = Th(cell)
        self.append_child(cell)

    def append_data_cell(self, cell):
        if not isinstance(cell, Td):
            cell = Td(cell)
        self.append_child(cell)

    def append_header_cells(self, *cells):
        for cell in cells:
            self.append_header_cell(cell)

    def append_data_cells(self, *cells):
        for cell in cells:
            self.append_data_cell(cell)


class Track(_HTMLNewlineVoidElement):
    TAG = 'track'


class U(_HTMLSamelineElement):
    TAG = 'u'


class Ul(_List):
    TAG = 'ul'


class Var(_HTMLSamelineElement):
    TAG = 'var'


class Video(_HTMLNewlineElement):
    TAG = 'video'


class Wbr(_HTMLSamelineElement):
    TAG = 'wbr'
