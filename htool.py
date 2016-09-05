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

from collections import OrderedDict
import itertools
import html


# TODO: Document that this function can be customised by overriding it globally
#       at the module level, or for each object by setting the 'ESCAPE_*'
#       attributes
def ESCAPE(rawtext):
    # TODO: Make this smart and leave already-escaped text as is, e.g.
    #       named character references (e.g. '&gt;')
    #       Probably use the html.entities.html5 dictionary
    return html.escape(rawtext)

ESCAPE_TEXT = None
ESCAPE_ATTR_NAME = None
ESCAPE_ATTR_VALUE = None


class _Element:
    # TODO: Document that when the class attributes are overridden, also a
    #       'self' argument must be accepted; when overriding the global
    #       attributes, or monkey-patching the self.escape_* object attributes,
    #       only the 'rawtext' argument is needed
    ESCAPE = None
    ESCAPE_TEXT = None
    ESCAPE_ATTR_NAME = None
    ESCAPE_ATTR_VALUE = None

    def __init__(self):
        self.parent_element = None
        self.escape_text = (self.ESCAPE_TEXT or self.ESCAPE or ESCAPE_TEXT or
                            ESCAPE)
        self.escape_attr_name = (self.ESCAPE_ATTR_NAME or self.ESCAPE or
                                 ESCAPE_ATTR_NAME or ESCAPE)
        self.escape_attr_value = (self.ESCAPE_ATTR_VALUE or self.ESCAPE or
                                  ESCAPE_ATTR_VALUE or ESCAPE)

    def compile(self):
        raise NotImplementedError()


class Doctype(_Element):
    def compile(self):
        return '<!doctype html>'


class RawText(_Element):
    def __init__(self, *text):
        super().__init__()
        self.text = ''.join(text)

    def compile(self):
        return self.text


class Comment(_Element):
    def __init__(self, *text):
        super().__init__()
        self.text = ''.join(text)

    def compile(self):
        # TODO: Does text have to be escaped?
        # TODO: Optionally surround text with spaces?
        return self.text.join(('<!--', '-->'))


class _TextNode(_Element):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def compile(self):
        return self.parent_element.escape_text(str(self.text))


class _HTMLElement(_Element):
    TAG = None
    ATTRIBUTES = OrderedDict()

    def __init__(self, **attributes):
        super().__init__()
        self.tag = self.TAG
        self.attributes = OrderedDict()
        self.attributes.update(self.ATTRIBUTES)

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

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_attributes(self, **attributes):
        # 'attributes' is still an unordered dict here, i.e. adding it unsorted
        # would make the key order variable from one run to the other
        self.attributes.update(sorted(attributes.items()))

    def add_class(self, name):
        # Prevent duplication; duplicate classes can be forced with
        # set_attribute
        # Do not use a set, or the class order will be lost (not meaningful,
        # but would create different html output every time)
        classes = self.attributes.get('class', '').split()
        if name not in classes:
            classes.append(name)
            self.set_attribute('class', ' '.join(classes))

    def _compose_start_tag(self):
        if self.attributes:
            attributes = ' '.join(
                '='.join((self.escape_attr_name(str(key)),
                          '"{}"'.format(self.escape_attr_value(str(value)))))
                for key, value in self.attributes.items())
            return ' '.join((self.tag, attributes))
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
            element = _TextNode(element)
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
    ESCAPE_TEXT = lambda self, rawtext: rawtext

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


class Document:
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
    def __init__(self, title, description, *body_elements, lang='en',
                 base=None, css=None, style=None, js=None):
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
