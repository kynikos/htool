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

from collections import OrderedDict
import itertools
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

# TODO: Document that the _Text classes to be used can be also set by
#       overriding the global 'DEFAULT_ESCAPE_*' module attributes, or for each
#       object by setting its 'DEFAULT_ESCAPE_*' attributes
DEFAULT_ESCAPE = None
DEFAULT_ESCAPE_TEXT = None
DEFAULT_ESCAPE_ATTR_NAME = None
DEFAULT_ESCAPE_ATTR_VALUE = None


class _Node(object):
    def __init__(self):
        # parent_element is modified directly, it isn't set with an __init__
        # parameter because positional arguments should be left only to
        # represent elements
        self.parent_element = None

    def compile(self):
        raise NotImplementedError()


class Doctype(_Node):
    def compile(self):
        return '<!doctype html>'


class _TextNode(_Node):
    def __init__(self, parent_element, text):
        super().__init__()
        self.parent_element = parent_element
        self.text = text if isinstance(
            text, _Text) else self.parent_element.DefaultContentEscape(text)

    def compile(self):
        return self.text.escaped


class _Element(_Node):
    # TODO: Document that when the class attributes are overridden, also a
    #       'self' argument must be accepted; when overriding the global
    #       attributes, or monkey-patching the self.escape_* object attributes,
    #       only the 'rawtext' argument is needed
    #       Note that this was tested when escaping was done with simple
    #       functions at compilation time; now that it's done with the _Text
    #       classes at instance creation, things may have changed
    DEFAULT_ESCAPE = None
    DEFAULT_ESCAPE_TEXT = None
    DEFAULT_ESCAPE_ATTR_NAME = None
    DEFAULT_ESCAPE_ATTR_VALUE = None

    def __init__(self):
        super().__init__()
        # TODO: Test this "inheritance" system again, since it was reorganized
        #       with the _Text classes
        self.DefaultContentEscape = (self.DEFAULT_ESCAPE_TEXT or
                                     self.DEFAULT_ESCAPE or
                                     DEFAULT_ESCAPE_TEXT or
                                     DEFAULT_ESCAPE or
                                     TextEscaped)
        self.DefaultAttributeNameEscape = (self.DEFAULT_ESCAPE_ATTR_NAME or
                                           self.DEFAULT_ESCAPE or
                                           DEFAULT_ESCAPE_ATTR_NAME or
                                           DEFAULT_ESCAPE or
                                           TextEscaped)
        self.DefaultAttributeValueEscape = (self.DEFAULT_ESCAPE_ATTR_VALUE or
                                            self.DEFAULT_ESCAPE or
                                            DEFAULT_ESCAPE_ATTR_VALUE or
                                            DEFAULT_ESCAPE or
                                            TextEscaped)


class Comment(_Element):
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


class _HTMLElement(_Element):
    TAG = None
    # Note that the structure of ATTRIBUTES is different from self.attributes
    # TODO: Document that these attributes are normally escaped
    ATTRIBUTES = OrderedDict()

    def __init__(self, **attributes):
        super().__init__()
        self.tag = self.TAG
        # TODO: Document that duplicate attribute names are not supported
        #       (i.e. setting an attribute with a certain name always
        #       overwrites if the name already exists)
        self.attributes = OrderedDict()
        # Don't use self.set_attributes because that's re-sorting the keys
        for name, value in self.ATTRIBUTES.items():
            self.set_attribute(name, value)

        # 'class' is a reserved Python keyword, so support using 'class_' and
        # 'classes'
        # TODO: Document this, including the fact that it's not possible to
        #       assign literal 'class_' or 'classes' attributes from keyword,
        #       as they will always be converted; suggest to use set_attribute
        #       in that case, and for other attributes such as 'data-*', or
        #       Tag(**{'class': 'name'})
        #       Also document that duplicate classes are automatically removed,
        #       and, again, using set_attribute is the way to force them
        # Note that a 'class' parameter can still be passed directly with e.g.
        # Tag(**{'class': 'name'}), so make sure to no override it here
        classnames = attributes.get('class', '').split()
        classnames.extend(attributes.get('class_', '').split())
        attributes.pop('class_', None)
        classnames.extend(attributes.get('classes', []))
        attributes.pop('classes', None)
        for cname in classnames:
            self.add_class(cname)

        self.set_attributes(**attributes)

    def get_attribute(self, name):
        return self.attributes[name][1].raw

    def set_attribute(self, name, value):
        if not isinstance(name, _Text):
            name = self.DefaultAttributeNameEscape(name)
        if not isinstance(value, _Text):
            value = self.DefaultAttributeValueEscape(value)
        self.attributes[name.escaped] = (name, value)

    def set_attributes(self, **attributes):
        # 'attributes' is still an unordered dict here, i.e. adding it unsorted
        # would make the key order variable from one run to the other
        for name, value in sorted(attributes.items()):
            self.set_attribute(name, value)

    def add_class(self, cname):
        # Prevent duplication; duplicate classes can be forced with
        # set_attribute
        # Do not use a set, or the class order will be lost (not meaningful,
        # but would create different html output every time)
        try:
            class_ = self.get_attribute('class')
        except KeyError:
            classes = []
        else:
            classes = class_.split()
        if not isinstance(cname, _Text):
            cname = self.DefaultAttributeValueEscape(cname)
        if cname.escaped not in classes:
            classes.append(cname.escaped)
            self.set_attribute('class', ' '.join(classes))

    def _compose_start_tag(self):
        if self.attributes:
            attributes = ''
            for escname, (name, value) in self.attributes.items():
                escvalue = '"{}"'.format(value.escaped)
                attribute = '='.join((escname, escvalue))
                attributes = ' '.join((attributes, attribute))
            return ''.join((self.tag, attributes))
        else:
            return self.tag


class _HTMLVoidElement(_HTMLElement):
    def compile(self):
        return '<{} />'.format(self._compose_start_tag())


class ElementContainer(_Element):
    def __init__(self, *children):
        super().__init__()
        self.children = []
        self.append_children(*children)

    def _prepare_child(self, element):
        if not isinstance(element, _Element):
            element = _TextNode(self, element)
        else:
            element.parent_element = self
        return element

    def prepend_child(self, element):
        self.children.insert(0, self._prepare_child(element))

    def append_child(self, element):
        # Accept (and safely ignore) None elements, so that they can be
        # added to parents with e.g. ternary operators, as in
        # P('foo', Span('bar') if abc else None)
        if element is not None:
            self.children.append(self._prepare_child(element))

    def append_children(self, *elements):
        for element in elements:
            self.append_child(element)

    def empty(self):
        self.children.clear()

    def compile(self):
        return '\n'.join(child.compile() for child in self.children)


class _HTMLNormalElement(_HTMLElement, ElementContainer):
    INDENTATION = ' ' * 4

    def __init__(self, *children, **attributes):
        _HTMLElement.__init__(self, **attributes)
        ElementContainer.__init__(self, *children)

    def compile(self):
        start = '<{}>'.format(self._compose_start_tag())
        content = ElementContainer.compile(self)
        if not self.children or (len(self.children) == 1 and
                                 isinstance(self.children[0], _TextNode)):
            sep = ''
        else:
            sep = '\n'
            content = ''.join((self.INDENTATION,
                               content.replace('\n', ''.join((
                                                    '\n', self.INDENTATION)))))
        end = '</{}>'.format(self.tag)
        return sep.join((start, content, end))


class _List(_HTMLNormalElement):
    def append_item(self, item):
        if not isinstance(item, Li):
            item = Li(item)
        self.append_child(item)

    def append_items(self, *items):
        for item in items:
            self.append_item(item)


class _Table(_HTMLNormalElement):
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


class Base(_HTMLVoidElement):
    TAG = 'base'


class Body(_HTMLNormalElement):
    TAG = 'body'


class Caption(_HTMLNormalElement):
    TAG = 'caption'


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


class Col(_HTMLVoidElement):
    TAG = 'col'


class Div(_HTMLNormalElement):
    TAG = 'div'


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


class Html(_HTMLNormalElement):
    TAG = 'html'


class Hr(_HTMLVoidElement):
    TAG = 'hr'


class Img(_HTMLVoidElement):
    TAG = 'img'


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


class Meta(_HTMLVoidElement):
    TAG = 'meta'


class Noscript(_HTMLNormalElement):
    TAG = 'noscript'


class Object(_HTMLNormalElement):
    TAG = 'object'


class Ol(_List):
    TAG = 'ol'


class Option(_HTMLNormalElement):
    TAG = 'option'


class P(_HTMLNormalElement):
    TAG = 'p'


class Param(_HTMLVoidElement):
    TAG = 'param'


class Script(_HTMLNormalElement):
    TAG = 'script'
    # TODO: Document that the text isn't escaped in this case
    DEFAULT_ESCAPE_TEXT = TextRaw

    @classmethod
    def js(cls, *children, **attributes):
        return cls(*children, type='text/javascript', **attributes)


class Select(_HTMLNormalElement):
    TAG = 'select'


class Span(_HTMLNormalElement):
    TAG = 'span'


class Strong(_HTMLNormalElement):
    TAG = 'strong'


class Style(_HTMLNormalElement):
    TAG = 'style'


class Table(_Table):
    TAG = 'table'


class Tbody(_Table):
    TAG = 'tbody'


class Td(_HTMLNormalElement):
    TAG = 'td'


class Tfoot(_Table):
    TAG = 'tfoot'


class Th(_HTMLNormalElement):
    TAG = 'th'


class Thead(_Table):
    TAG = 'thead'


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


class Ul(_List):
    TAG = 'ul'


class Document(object):
    def __init__(self, html, doctype=Doctype()):
        self.doctype = doctype
        self.html = html

    def compile(self):
        return '\n'.join((self.doctype.compile(), self.html.compile()))

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(self.compile().encode('ascii', 'xmlcharrefreplace'
                                          ).decode('utf-8'))


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
        super().__init__(html)
