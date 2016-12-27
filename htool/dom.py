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

from collections import OrderedDict

from .text import _Text, TextEscaped

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

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(self.compile())


class _TextNode(_Node):
    def __init__(self, parent_element, text):
        super(_TextNode, self).__init__()
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
        super(_Element, self).__init__()
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


class _HTMLElement(_Element):
    TAG = None
    # Note that the structure of ATTRIBUTES is different from self.attributes
    # TODO: Document that these attributes are normally escaped
    ATTRIBUTES = OrderedDict()

    def __init__(self, **attributes):
        super(_HTMLElement, self).__init__()
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
                escvalue = '"{0}"'.format(value.escaped)
                attribute = '='.join((escname, escvalue))
                attributes = ' '.join((attributes, attribute))
            return ''.join((self.tag, attributes))
        else:
            return self.tag


class _HTMLVoidElement(_HTMLElement):
    def compile(self):
        return '<{0} />'.format(self._compose_start_tag())


class _ElementContainer(_Element):
    GLUE = '\n'

    def __init__(self, *children):
        super(_ElementContainer, self).__init__()
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
        return self.GLUE.join(child.compile() for child in self.children)


class _HTMLNormalElement(_HTMLElement, _ElementContainer):
    # TODO: Allow resetting the indentation from a particular node in the tree
    INDENTATION = ' ' * 4

    def __init__(self, *children, **attributes):
        _HTMLElement.__init__(self, **attributes)
        _ElementContainer.__init__(self, *children)

    def compile(self):
        start = '<{0}>'.format(self._compose_start_tag())
        content = _ElementContainer.compile(self)
        # TODO: Allow customizing the glueing between elements
        if not self.children or (len(self.children) == 1 and
                                 isinstance(self.children[0], _TextNode)):
            sep = ''
        else:
            sep = self.GLUE
            # BUG: If the glue is an empty string, this will still insert the
            #      indentation before the content
            content = ''.join((self.INDENTATION,
                               content.replace('\n', ''.join((
                                                    '\n', self.INDENTATION)))))
        end = '</{0}>'.format(self.tag)
        return sep.join((start, content, end))
