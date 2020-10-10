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
    BREAK_BEFORE = False
    BREAK_AFTER = False

    def __init__(self):
        # parent_element is modified directly, it isn't set with an __init__
        # parameter because positional arguments should be left only to
        # represent elements
        # BUG: What happens if an element object is added as a child of two or
        #      more different parent element objects?
        self.parent_element = None

    def compile(self, indent=""):
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

    def compile(self, indent=""):
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

        # TODO: Make sure to properly document the following behavior
        #       Also document that duplicate classes are automatically removed,
        #       and using set_attribute() is the way to force them
        # If in need of overriding this behavior, use set_attribute() or
        # Tag(**{'-attr-foo_bar-': 'value'})
        # 'classes' is a special attribute (this can be overridden by passing
        # classes_="value", Classes="value", **{"classes_": "value"}, etc.)
        # Note that 'classes' can't be a tuple, it must be a list!
        classnames = attributes.pop('classes', [])
        for attrname, attrval in tuple(attributes.items()):
            # If an attribute ends with an underscore, the underscore is
            # removed and the rest of the attribute name is used as is; this is
            # useful for example with 'class' and 'for', which are common HTML
            # attributes but also reserved Python keywords; if an attribute is
            # passed both with and without a trailing underscore, the two are
            # left as they are
            # If in need to keep the final underscore, just double it, e.g.
            # attr__="value"
            if attrname.endswith("_"):
                attrname_ = attrname[:-1]
                if attrname_ not in attributes:
                    attributes[attrname_] = attributes.pop(attrname)
            # Else all underscores are changed into dashes, and the attribute
            # name is converted to lowercase; this is useful for example with
            # 'class' and 'for' (use Class="value", For="value"...) and the
            # 'data-*' attributes; if however the "dashed" attribute name
            # already exists, leave the two as they are
            else:
                attrname_ = attrname.replace("_", "-").lower()
                if attrname_ not in attributes:
                    attributes[attrname_] = attributes.pop(attrname)
        classnames.extend(attributes.get('class', '').split())
        self.add_classes(*classnames)

        self.set_attributes(**attributes)

    @classmethod
    def join(cls, *elements, **attributes):
        """
        This method works like Python's str.join(), for example:

            Br.join(*elements)

        """
        from .misc import ElementContainer
        container = ElementContainer()
        if elements:
            ielements = iter(elements)
            for element in ielements:
                if element is not None:
                    container.append_children(element)
                    break
            for element in ielements:
                if element is not None:
                    container.append_children(cls(**attributes), element)
            return container

    def get_attribute(self, name):
        value = self.attributes[name][1]
        if value is not None:
            return value.raw
        return value

    def set_attribute(self, name, value):
        # TODO: HTML attributes are case-insensitive, force lowercase here?
        #       Note that currently lower() is applied to attributes in the
        #       constructor: if added here, it must be removed from the
        #       constructor, since it would be redundant
        if not isinstance(name, _Text):
            name = self.DefaultAttributeNameEscape(name)
        # A value of None should create attributes without values
        # TODO: Document this
        if value is not None and not isinstance(value, _Text):
            value = self.DefaultAttributeValueEscape(value)
        self.attributes[name.escaped] = (name, value)

    def set_attributes(self, **attributes):
        # 'attributes' is still an unordered dict here, i.e. adding it unsorted
        # would make the key order variable from one run to the other
        for name, value in sorted(attributes.items()):
            self.set_attribute(name, value)

    def add_class(self, cname):
        return self.add_classes(*cname.split())

    def add_classes(self, *cnames):
        # Prevent duplication; duplicate classes can be forced with
        # set_attribute
        # Do *not* use a set, or the class order will be lost (not meaningful,
        # but would create different html output every time)
        try:
            class_ = self.get_attribute('class')
        except KeyError:
            classes = []
        else:
            classes = class_.split()
        for cname in cnames:
            if not isinstance(cname, _Text):
                cname = self.DefaultAttributeValueEscape(cname)
            if cname.escaped not in classes:
                classes.append(cname.escaped)
        if classes:
            self.set_attribute('class', ' '.join(classes))

    def _compose_start_tag(self):
        if self.attributes:
            attributes = ''
            for escname, (name, value) in self.attributes.items():
                if value is None:
                    attribute = escname
                else:
                    escvalue = value.escaped.join(('"', '"'))
                    attribute = '='.join((escname, escvalue))
                attributes = ' '.join((attributes, attribute))
            return ''.join((self.tag, attributes))
        else:
            return self.tag


class _HTMLVoidElement(_HTMLElement):
    def compile(self, indent=""):
        return self._compose_start_tag().join(('<', ' />'))


class _ElementContainer(_Element):
    # TODO: Allow resetting the indentation from a particular node in the tree
    INDENTATION = ''

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

    def compile(self, indent=""):
        try:
            prevchild = self.children[0]
        except IndexError:
            return ""

        subindent = "".join((indent, self.INDENTATION))
        # The first child's BREAK_BEFORE is taken into account in
        # _HTMLContainerElement.compile()
        compiled = prevchild.compile(indent=subindent)
        for child in self.children[1:]:
            if prevchild.BREAK_AFTER or child.BREAK_BEFORE:
                compiled = "".join((compiled, "\n", subindent))
            compiled = "".join((compiled, child.compile(indent=subindent)))
            prevchild = child
        # The last child's BREAK_AFTER is taken into account in
        # _HTMLContainerElement.compile()
        return compiled


class _HTMLContainerElement(_HTMLElement, _ElementContainer):
    INDENTATION = ' ' * 2
    # NOTE[1]: By default do not force indentation on multiline text, because
    # some elements like <pre> or <textarea> preserve white space (also leading
    # and trailing); CSS behavior is influenced too in many inline elements
    # See also
    # https://stackoverflow.com/questions/27025877/are-leading-and-trailing-whitespaces-ignored-in-html
    AUTOINDENT_MULTILINE = False

    def __init__(self, *children, **attributes):
        _HTMLElement.__init__(self, **attributes)
        _ElementContainer.__init__(self, *children)

    def compile(self, indent=""):
        # The start tag is indented by the partent _ElementContainer if needed
        start = self._compose_start_tag().join(('<', '>'))
        # The content is indented by _ElementContainer.compile()
        content = _ElementContainer.compile(self, indent=indent)
        end = self.tag.join(('</', '>'))
        # See NOTE[1]
        # Do not just test if there are children with a BREAK_* attribute,
        # since also all the descendants should be tested and the code would
        # get much more complicated
        if self.AUTOINDENT_MULTILINE and "\n" in content:
            start = "".join((start, "\n", indent, self.INDENTATION))
            end = "".join(("\n", indent, end))
        else:
            try:
                first_child = self.children[0]
            except IndexError:
                pass
            else:
                if first_child.BREAK_BEFORE:
                    # The first child's BREAK_BEFORE has not been taken into
                    # account in _ElementContainer.compile(), so do it here
                    start = "".join((start, "\n", indent, self.INDENTATION))
                if self.children[-1].BREAK_AFTER:
                    # The last child's BREAK_AFTER has not been taken into
                    # account in _ElementContainer.compile(), so do it here
                    end = "".join(("\n", indent, end))
        return "".join((start, content, end))


class _HTMLNewlineVoidElement(_HTMLVoidElement):
    BREAK_BEFORE = True
    BREAK_AFTER = True
    AUTOINDENT_MULTILINE = True


class _HTMLNewlineElement(_HTMLContainerElement):
    BREAK_BEFORE = True
    BREAK_AFTER = True
    AUTOINDENT_MULTILINE = True


class _HTMLPrelineVoidElement(_HTMLVoidElement):
    BREAK_BEFORE = True
    BREAK_AFTER = True
    AUTOINDENT_MULTILINE = False


class _HTMLPrelineElement(_HTMLContainerElement):
    BREAK_BEFORE = True
    BREAK_AFTER = True
    AUTOINDENT_MULTILINE = False


class _HTMLStartlineVoidElement(_HTMLVoidElement):
    BREAK_BEFORE = True
    BREAK_AFTER = False
    AUTOINDENT_MULTILINE = False


class _HTMLStartlineElement(_HTMLContainerElement):
    BREAK_BEFORE = True
    BREAK_AFTER = False
    AUTOINDENT_MULTILINE = False


class _HTMLEndlineVoidElement(_HTMLVoidElement):
    BREAK_BEFORE = False
    BREAK_AFTER = True
    AUTOINDENT_MULTILINE = False


class _HTMLEndlineElement(_HTMLContainerElement):
    BREAK_BEFORE = False
    BREAK_AFTER = True
    AUTOINDENT_MULTILINE = False


class _HTMLSamelineVoidElement(_HTMLVoidElement):
    BREAK_BEFORE = False
    BREAK_AFTER = False
    AUTOINDENT_MULTILINE = False


class _HTMLSamelineElement(_HTMLContainerElement):
    BREAK_BEFORE = False
    BREAK_AFTER = False
    AUTOINDENT_MULTILINE = False
