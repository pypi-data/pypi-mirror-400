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

"""PyAMS_utils.dict module

This helper module only contains a single function which can be used to update an input
dictionary; if given value argument is a boolean 'true' value, given dictionary's key is created
or updated, otherwise dictionary is left unchanged.
"""

from html import escape

__docformat__ = 'restructuredtext'


class DotDict(dict):
    """A utility class which behaves like a dict, but also allows dot-access to keys
    
    >>> from pyams_utils.dict import DotDict
    >>> mydict = DotDict({'key1': 'Value 1'})
    >>> mydict
    <DotDict({'key1': 'Value 1'})>
    >>> mydict.key1
    'Value 1'
    >>> mydict.key2
    Traceback (most recent call last):
    ...
    KeyError: 'key2'
    
    Inner lists or mappings, if any, are also converted to DotDict class:
    
    >>> mydict = DotDict({'key1': {'key2': 'Value 2'}})
    >>> mydict
    <DotDict({'key1': <DotDict({'key2': 'Value 2'})>})>
    >>> mydict.key1.key2
    'Value 2'
    
    >>> mydict = DotDict({'key1': [{'key2': 'Value 2'}]})
    >>> mydict
    <DotDict({'key1': [<DotDict({'key2': 'Value 2'})>]})>
    >>> mydict.key1[0].key2
    'Value 2'
    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    __conform__ = None

    def __init__(self, d=None):  # pylint: disable=super-init-not-called
        if d is None:
            d = {}
        for key, value in d.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            if isinstance(value, list):
                value = [
                    DotDict(el) if hasattr(el, 'keys') else el
                    for el in value
                ]
            self[key] = value

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, dict.__repr__(self))


def update_dict(input_dict: dict, key, value):
    """Update given mapping if input value is a boolean 'True' value

    :param dict input_dict: input dictionary
    :param key: mapping key
    :param value: new value

    'False' values leave mapping unchanged::

    >>> from pyams_utils.dict import update_dict
    >>> mydict = {}
    >>> update_dict(mydict, 'key1', None)
    >>> mydict
    {}
    >>> update_dict(mydict, 'key1', '')
    >>> mydict
    {}
    >>> update_dict(mydict, 'key1', 0)
    >>> mydict
    {}

    'True' values modify the mapping::

    >>> update_dict(mydict, 'key1', 'value')
    >>> mydict
    {'key1': 'value'}
    >>> update_dict(mydict, 'key1', 'value2')
    >>> mydict
    {'key1': 'value2'}
    """
    if value:
        input_dict[key] = value


def merge_dict(source: dict, target: dict):
    """Deep merge of source mapping into target mapping

    >>> from pyams_utils.dict import merge_dict
    >>> trg = {}
    >>> merge_dict({}, trg)
    {}
    >>> merge_dict({'key 1': 'value'}, trg)
    {'key 1': 'value'}
    >>> merge_dict({'key 1': 'value 1'}, trg)
    {'key 1': 'value 1'}
    >>> merge_dict({'key 2': {'subkey 1': 'subvalue 1'}}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 1'}}
    >>> merge_dict({'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}}
    >>> merge_dict({'key 3': ['Value 4']}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}, \
     'key 3': ['Value 4']}
    >>> merge_dict({'key 3': ['Value 5']}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}, \
     'key 3': ['Value 4', 'Value 5']}
    >>> merge_dict({'key 4': {'Value 6'}}, trg)
    {'key 1': 'value 1', 'key 2': {'subkey 1': 'subvalue 2', 'subkey 2': 'subvalue 3'}, \
     'key 3': ['Value 4', 'Value 5'], 'key 4': {'Value 6'}}
    >>> sorted(merge_dict({'key 4': {'Value 7'}}, trg)['key 4'])
    ['Value 6', 'Value 7']
    """
    for key, value in source.items():
        if key in target:
            if isinstance(target[key], (list, tuple)):
                target[key] += source[key]
            elif isinstance(target[key], set):
                target[key] |= source[key]
            elif isinstance(target[key], dict):
                target[key].update(value)
            else:
                target[key] = value
        else:
            target[key] = value
    return target


def format_dict(input_dict: dict):
    """Dict string formatter

    >>> from collections import OrderedDict
    >>> from pyams_utils.dict import format_dict
    >>> input = {}
    >>> format_dict(input)
    '{}'
    >>> input = OrderedDict((('key1', 'Value 1'), ('key2', 'Value 2'),))
    >>> print(format_dict(input))
    {
        key1: Value 1
        key2: Value 2
    }
    """
    if not input_dict:
        return '{}'
    return "{{\n{}\n}}".format('\n'.join(('    {}: {}'.format(key, value)
                                         for key, value in input_dict.items())))


def escape_dict(value, in_place=False):
    """Escape all values from input dictionary, leaving input unchanged

    >>> from pyams_utils.dict import escape_dict
    >>> input = {
    ...     'key1': '<value1 />',
    ...     'key2': {'key3': 'value2&value3'},
    ...     'key4': ['<value4 />'],
    ...     'key5': set(['<value5 />']),
    ...     'key6': 6
    ... }
    >>> escape_dict(input)
    {'key1': '&lt;value1 /&gt;', 'key2': {'key3': 'value2&amp;value3'}, 'key4': ['&lt;value4 /&gt;'], 'key5': {'&lt;value5 /&gt;'}, 'key6': 6}

    Initial value is not modified::
    >>> input
    {'key1': '<value1 />', 'key2': {'key3': 'value2&value3'}, 'key4': ['<value4 />'], 'key5': {'<value5 />'}, 'key6': 6}

    >>> escape_dict(input, in_place=True)
    {'key1': '&lt;value1 /&gt;', 'key2': {'key3': 'value2&amp;value3'}, 'key4': ['&lt;value4 /&gt;'], 'key5': {'&lt;value5 /&gt;'}, 'key6': 6}
    >>> input
    {'key1': '&lt;value1 /&gt;', 'key2': {'key3': 'value2&amp;value3'}, 'key4': ['&lt;value4 /&gt;'], 'key5': {'&lt;value5 /&gt;'}, 'key6': 6}
    """
    result = value if in_place else {}
    for key, val in value.items():
        if isinstance(val, str):
            result[key] = escape(val)
        elif isinstance(val, dict):
            result[key] = escape_dict(val)
        elif isinstance(val, list):
            result[key] = [
                escape_dict(item) if isinstance(item, dict) else escape(item)
                for item in val
            ]
        elif isinstance(val, set):
            result[key] = {
                escape_dict(item) if isinstance(item, dict) else escape(item)
                for item in val
            }
        else:
            result[key] = val
    return result


def boolean_dict(input_dict: dict):
    """Dict values checker

    Returns a true value if at least one dict value is true.

    >>> from pyams_utils.dict import boolean_dict
    >>> input = {}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': 0}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': ''}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': None}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': []}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': {}}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': set()}
    >>> boolean_dict(input)
    False
    >>> input = {'key1': 1}
    >>> boolean_dict(input)
    True
    >>> input = {'key1': 'value1'}
    >>> boolean_dict(input)
    True
    >>> input = {'key1': 1, 'key2': ''}
    >>> boolean_dict(input)
    True
    """
    if not input_dict:
        return False
    for value in input_dict.values():
        if value:
            return True
    return False
