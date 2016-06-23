import itertools


class _Element:
    def compose(self):
        raise NotImplementedError()


class Doctype(_Element):
    def compose(self):
        return '<!doctype html>'


class _HTMLElement(_Element):
    TAG = None
    ATTRIBUTES = {}

    def __init__(self, **attributes):
        super().__init__()
        self.tag = self.TAG
        self.attributes = self.ATTRIBUTES.copy()

        # 'class' is a reserved Python keyword, so support using 'class_' and
        # 'classes'
        # TODO: Document this, including the fact that it's not possible to
        #       assign literal 'class_' or 'classes' attributes, as they will
        #       always be converted
        # Note that a 'class' parameter can still be passed directly with e.g.
        # Tag(**{'class': 'name'})
        classnames = attributes.get('class', '').split()
        classnames.extend(attributes.get('class_', '').split())
        attributes.pop('class_', None)
        classnames.extend(attributes.get('classes', []))
        attributes.pop('classes', None)
        if classnames:
            attributes['class'] = ' '.join(classnames)

        self.attributes.update(attributes)

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_attributes(self, **attributes):
        self.attributes.update(attributes)

    def _compose_start_tag(self):
        if self.attributes:
            attributes = ' '.join('='.join((key, '"{}"'.format(value)))
                                  for key, value in
                                  sorted(self.attributes.items()))
            return ' '.join((self.tag, attributes))
        else:
            return self.tag


class _HTMLVoidElement(_HTMLElement):
    def compose(self):
        return '<{} />'.format(self._compose_start_tag())


class _TextNode(_Element):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def compose(self):
        return self.text


class ElementContainer(_Element):
    def __init__(self, *children):
        super().__init__()
        self.children = []
        self.append_children(*children)

    def prepend_child(self, element):
        if not isinstance(element, _Element):
            element = _TextNode(element)
        self.children.insert(0, element)

    def append_child(self, element):
        if not isinstance(element, _Element):
            element = _TextNode(element)
        self.children.append(element)

    def append_children(self, *elements):
        for element in elements:
            self.append_child(element)

    def empty(self):
        self.children.clear()

    def compose(self):
        return '\n'.join(child.compose() for child in self.children)


class _HTMLNormalElement(_HTMLElement, ElementContainer):
    INDENTATION = ' ' * 4

    def __init__(self, *children, **attributes):
        _HTMLElement.__init__(self, **attributes)
        ElementContainer.__init__(self, *children)

    def compose(self):
        start = '<{}>'.format(self._compose_start_tag())
        content = ElementContainer.compose(self)
        if not self.children or (len(self.children) == 1 and
                                 isinstance(self.children[0], _TextNode)):
            sep = ''
        else:
            sep = '\n'
            content = ''.join((self.INDENTATION,
                               content.replace('\n', ''.join(('\n',
                                                          self.INDENTATION)))))
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


class Li(_HTMLNormalElement):
    TAG = 'li'


class Link(_HTMLVoidElement):
    TAG = 'link'

    @classmethod
    def css(cls, path, **attributes):
        return cls(href=path, rel="stylesheet", **attributes)


class Meta(_HTMLVoidElement):
    TAG = 'meta'


class Ol(_List):
    TAG = 'ol'


class Option(_HTMLNormalElement):
    TAG = 'option'


class P(_HTMLNormalElement):
    TAG = 'p'


class Script(_HTMLNormalElement):
    TAG = 'script'

    @classmethod
    def js(cls, **attributes):
        return cls(type='text/javascript', **attributes)


class Select(_HTMLNormalElement):
    TAG = 'select'


class Span(_HTMLNormalElement):
    TAG = 'span'


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

    def compose(self):
        return '\n'.join((self.doctype.compose(), self.html.compose()))

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(self.compose().encode('ascii', 'xmlcharrefreplace'
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
            for path in css:
                head.append_child(Link.css(path))
        if style is not None:
            head.append_child(Style(style))
        if js is not None:
            for path in js:
                head.append_child(Script.js(src=path))

        body = Body(*body_elements)

        html.append_children(head, body)
        super().__init__(html)
