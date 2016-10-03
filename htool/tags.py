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
# from builtins import *

import itertools

from .dom import _HTMLVoidElement, _HTMLNormalElement
from .text import TextRaw


class _List(_HTMLNormalElement):
    # This class is too coupled with this module to be moved to a separate one
    def append_item(self, item):
        if not isinstance(item, Li):
            item = Li(item)
        self.append_child(item)

    def append_items(self, *items):
        for item in items:
            self.append_item(item)


class _Table(_HTMLNormalElement):
    # This class is too coupled with this module to be moved to a separate one
    def append_header_row(self, *cells):
        row = Tr()
        self.append_child(row)
        row.append_header_cells(*cells)

    def append_data_row(self, *cells):
        row = Tr()
        self.append_child(row)
        row.append_data_cells(*cells)

    def append_header_rows(self, *rows):
        for row in rows:
            self.append_header_row(*row)

    def append_data_rows(self, *rows):
        for row in rows:
            self.append_data_row(*row)


class A(_HTMLNormalElement):
    TAG = 'a'

    @classmethod
    def from_url(cls, url, **attributes):
        return cls(url, href=url, **attributes)


class Abbr(_HTMLNormalElement):
    TAG = 'abbr'


class Address(_HTMLNormalElement):
    TAG = 'address'


class Area(_HTMLVoidElement):
    TAG = 'area'


class Article(_HTMLNormalElement):
    TAG = 'article'


class Aside(_HTMLNormalElement):
    TAG = 'aside'


class Audio(_HTMLNormalElement):
    TAG = 'audio'


class B(_HTMLNormalElement):
    TAG = 'b'


class Base(_HTMLVoidElement):
    TAG = 'base'


class Bdi(_HTMLNormalElement):
    TAG = 'bdi'


class Bdo(_HTMLNormalElement):
    TAG = 'bdo'


class Blockquote(_HTMLNormalElement):
    TAG = 'blockquote'


class Body(_HTMLNormalElement):
    TAG = 'body'


class Br(_HTMLVoidElement):
    TAG = 'br'


class Button(_HTMLNormalElement):
    TAG = 'button'


class Canvas(_HTMLNormalElement):
    TAG = 'canvas'


class Caption(_HTMLNormalElement):
    TAG = 'caption'


class Cite(_HTMLNormalElement):
    TAG = 'cite'


class Code(_HTMLNormalElement):
    TAG = 'code'


class Col(_HTMLVoidElement):
    TAG = 'col'


class Colgroup(_HTMLNormalElement):
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


class Data(_HTMLNormalElement):
    TAG = 'data'


class Datalist(_HTMLNormalElement):
    TAG = 'datalist'


class Dd(_HTMLNormalElement):
    TAG = 'dd'


class Del(_HTMLNormalElement):
    TAG = 'del'


class Details(_HTMLNormalElement):
    TAG = 'details'


class Dfn(_HTMLNormalElement):
    TAG = 'dfn'


class Dialog(_HTMLNormalElement):
    TAG = 'dialog'


class Div(_HTMLNormalElement):
    TAG = 'div'


class Dl(_HTMLNormalElement):
    TAG = 'dl'


class Dt(_HTMLNormalElement):
    TAG = 'dt'


class Em(_HTMLNormalElement):
    TAG = 'em'


class Embed(_HTMLVoidElement):
    TAG = 'embed'


class Fieldset(_HTMLNormalElement):
    TAG = 'fieldset'


class Figcaption(_HTMLNormalElement):
    TAG = 'figcaption'


class Figure(_HTMLNormalElement):
    TAG = 'figure'


class Footer(_HTMLNormalElement):
    TAG = 'footer'


class Form(_HTMLNormalElement):
    TAG = 'form'


class H1(_HTMLNormalElement):
    TAG = 'h1'


class H2(_HTMLNormalElement):
    TAG = 'h2'


class H3(_HTMLNormalElement):
    TAG = 'h3'


class H4(_HTMLNormalElement):
    TAG = 'h4'


class H5(_HTMLNormalElement):
    TAG = 'h5'


class H6(_HTMLNormalElement):
    TAG = 'h6'


class Head(_HTMLNormalElement):
    TAG = 'head'


class Header(_HTMLNormalElement):
    TAG = 'header'


class Hgroup(_HTMLNormalElement):
    TAG = 'hgroup'


class Hr(_HTMLVoidElement):
    TAG = 'hr'


class Html(_HTMLNormalElement):
    TAG = 'html'


class I(_HTMLNormalElement):
    TAG = 'i'


class Iframe(_HTMLNormalElement):
    TAG = 'iframe'


class Img(_HTMLVoidElement):
    TAG = 'img'


class Input(_HTMLVoidElement):
    TAG = 'input'


class Ins(_HTMLNormalElement):
    TAG = 'ins'


class Kbd(_HTMLNormalElement):
    TAG = 'kbd'


class Label(_HTMLNormalElement):
    TAG = 'label'


class Legend(_HTMLNormalElement):
    TAG = 'legend'


class Li(_HTMLNormalElement):
    TAG = 'li'


class Link(_HTMLVoidElement):
    TAG = 'link'

    @classmethod
    def css(cls, path, **attributes):
        return cls(href=path, type="text/css", rel="stylesheet", **attributes)

    @classmethod
    def favicon(cls, path, **attributes):
        return cls(href=path, rel="icon", **attributes)


class Main(_HTMLNormalElement):
    TAG = 'main'


class Map(_HTMLNormalElement):
    TAG = 'map'


class Mark(_HTMLNormalElement):
    TAG = 'mark'


class Menu(_HTMLNormalElement):
    TAG = 'menu'


class Menuitem(_HTMLNormalElement):
    TAG = 'menuitem'


class Meta(_HTMLVoidElement):
    TAG = 'meta'


class Meter(_HTMLNormalElement):
    TAG = 'meter'


class Nav(_HTMLNormalElement):
    TAG = 'nav'


class Noscript(_HTMLNormalElement):
    TAG = 'noscript'


class Object(_HTMLNormalElement):
    TAG = 'object'


class Ol(_List):
    TAG = 'ol'


class Optgroup(_HTMLNormalElement):
    TAG = 'optgroup'


class Option(_HTMLNormalElement):
    TAG = 'option'


class Output(_HTMLNormalElement):
    TAG = 'output'


class P(_HTMLNormalElement):
    TAG = 'p'


class Param(_HTMLVoidElement):
    TAG = 'param'


class Picture(_HTMLNormalElement):
    TAG = 'picture'


class Pre(_HTMLNormalElement):
    TAG = 'pre'


class Progress(_HTMLNormalElement):
    TAG = 'progress'


class Q(_HTMLNormalElement):
    TAG = 'q'


class Rp(_HTMLNormalElement):
    TAG = 'rp'


class Rt(_HTMLNormalElement):
    TAG = 'rt'


class Rtc(_HTMLNormalElement):
    TAG = 'rtc'


class Ruby(_HTMLNormalElement):
    TAG = 'ruby'


class S(_HTMLNormalElement):
    TAG = 's'


class Samp(_HTMLNormalElement):
    TAG = 'samp'


class Script(_HTMLNormalElement):
    TAG = 'script'
    # TODO: Document that the text isn't escaped in this case
    DEFAULT_ESCAPE_TEXT = TextRaw

    @classmethod
    def js(cls, *children, **attributes):
        return cls(*children, type='text/javascript', **attributes)


class Section(_HTMLNormalElement):
    TAG = 'section'


class Select(_HTMLNormalElement):
    TAG = 'select'


class Shadow(_HTMLNormalElement):
    TAG = 'select'


class Small(_HTMLNormalElement):
    TAG = 'small'


class Source(_HTMLVoidElement):
    TAG = 'source'


class Span(_HTMLNormalElement):
    TAG = 'span'


class Strong(_HTMLNormalElement):
    TAG = 'strong'


class Style(_HTMLNormalElement):
    TAG = 'style'


class Sub(_HTMLNormalElement):
    TAG = 'sub'


class Summary(_HTMLNormalElement):
    TAG = 'summary'


class Sup(_HTMLNormalElement):
    TAG = 'sup'


class Table(_Table):
    TAG = 'table'


class Tbody(_Table):
    TAG = 'tbody'


class Td(_HTMLNormalElement):
    TAG = 'td'


class Template(_HTMLNormalElement):
    TAG = 'template'


class Textarea(_HTMLNormalElement):
    TAG = 'textarea'


class Tfoot(_Table):
    TAG = 'tfoot'


class Th(_HTMLNormalElement):
    TAG = 'th'


class Thead(_Table):
    TAG = 'thead'


class Time(_HTMLNormalElement):
    TAG = 'time'


class Title(_HTMLNormalElement):
    TAG = 'title'


class Tr(_HTMLNormalElement):
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


class Track(_HTMLVoidElement):
    TAG = 'track'


class U(_HTMLNormalElement):
    TAG = 'u'


class Ul(_List):
    TAG = 'ul'


class Var(_HTMLNormalElement):
    TAG = 'var'


class Video(_HTMLNormalElement):
    TAG = 'video'


class Wbr(_HTMLNormalElement):
    TAG = 'wbr'
