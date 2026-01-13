#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.tales module

This module provides a custom TALES extension engine, which allows you to define custom
TALES expressions which can be used from Chameleon or Zope templates.
"""

import re

from chameleon.astutil import Symbol
from chameleon.codegen import template
from chameleon.tales import StringExpr
from zope.component import queryAdapter, queryMultiAdapter
from zope.contentprovider.tales import addTALNamespaceData

from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


class ContextExprMixin:
    """Mixin-class for expression compilers"""

    transform = None

    def __call__(self, target, engine):
        # Make call to superclass to assign value to target
        assignment = super().__call__(target, engine)
        transform = template("target = transform(econtext, target)",
                             target=target,
                             transform=self.transform)
        return assignment + transform


FUNCTION_EXPRESSION = re.compile(r'(.+)\((.+)\)', re.MULTILINE | re.DOTALL)
ARGUMENTS_EXPRESSION = re.compile(r'[^(,)]+')


def render_extension(econtext, name):
    """TALES extension renderer

    See :ref:`tales` for complete description.

    The requested extension can be called with our without arguments, like in
    ${structure:tales:my_expression} or ${structure:tales:my_expression(arg1, arg2)}.
    In the second form, arguments will be passed to the "render" method; arguments can be
    static (like strings or integers), or can be variables defined into current template
    context; other Python expressions including computations or functions calls are actually
    not supported, but dotted syntax is supported to access inner attributes of variables.
    """

    def get_value(econtext, arg):
        """Extract argument value from context

        Extension expression language is quite simple. Values can be given as
        positioned strings, integers or named arguments of the same types.
        """
        arg = arg.strip()
        if arg.startswith('"') or arg.startswith("'"):
            # may be a quoted string...
            return arg[1:-1]
        if '=' in arg:
            key, value = arg.split('=', 1)
            value = get_value(econtext, value)
            return {key.strip(): value}
        try:
            arg = int(arg)  # check integer value
        except ValueError:
            args = arg.split('.')
            result = econtext.get(args.pop(0))
            for arg in args:  # pylint: disable=redefined-argument-from-local
                result = getattr(result, arg)
            return result
        else:
            return arg

    name = name.strip()
    context = econtext.get('context')
    request = econtext.get('request')
    view = econtext.get('view')

    args, kwargs = [], {}
    func_match = FUNCTION_EXPRESSION.match(name)
    if func_match:
        name, arguments = func_match.groups()
        for arg in map(lambda x: get_value(econtext, x), ARGUMENTS_EXPRESSION.findall(arguments)):
            if isinstance(arg, dict):
                kwargs.update(arg)
            else:
                args.append(arg)

    extension = queryMultiAdapter((context, request, view), ITALESExtension, name=name)
    if extension is None:
        extension = queryMultiAdapter((context, request), ITALESExtension, name=name)
    if extension is None:
        extension = queryAdapter(context, ITALESExtension, name=name)

    # return an empty string if the extension was not found.
    if extension is None:
        return ''

    # Insert the data gotten from the context
    addTALNamespaceData(extension, econtext)

    return extension.render(*args, **kwargs)


class ExtensionExpr(ContextExprMixin, StringExpr):
    """tales: TALES expression

    This expression can be used to call a custom named adapter providing ITALESExtension interface.
    """

    transform = Symbol(render_extension)
