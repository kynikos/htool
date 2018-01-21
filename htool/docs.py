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

from .tags import Base, Body, Head, Html, Link, Meta, Script, Style, Title
from .misc import Doctype, ElementContainer


class Document(ElementContainer):
    def __init__(self, html, doctype=None):
        super(Document, self).__init__(doctype or Doctype(), html)


class SimpleDocument(Document):
    def __init__(self, title, description, *body_elements, **kwargs):
        # Python 2 must be supported, so the following definition can't be
        # used...
        # __init__(self, title, description, *body_elements, lang='en',
        #          base=None, css=None, style=None, js=None):
        lang = kwargs.pop('lang', 'en')
        base = kwargs.pop('base', None)
        css = kwargs.pop('css', None)
        style = kwargs.pop('style', None)
        js = kwargs.pop('js', None)

        html = Html(lang=lang)

        head = Head(Title(title),
                    Meta(charset='utf-8'),
                    Meta(name='description', content=description))
        if base is not None:
            head.append_child(Base(href=base))
        if css is not None:
            # Use a nested list, not a dictionary, or the sheet order will be
            # lost
            for media, path in css:
                head.append_child(Link.css(path, media=media))
        if style is not None:
            head.append_child(Style(style))
        if js is not None:
            for path in js:
                head.append_child(Script.js(src=path))

        body = Body(*body_elements)

        html.append_children(head, body)
        super(SimpleDocument, self).__init__(html)
