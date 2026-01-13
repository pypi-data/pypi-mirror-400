#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils package

PyAMS generic modules
"""

from fanstatic import Library
from zope.schema.fieldproperty import FieldProperty


__docformat__ = 'restructuredtext'


from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('pyams_utils')


library = Library('pyams', '.')


def get_field_doc(self):
    """Try to get FieldProperty field docstring from field interface"""
    field = self._FieldProperty__field  # pylint: disable=protected-access
    if field.title:
        if field.description:
            return f'{field.title}: {field.description}'
        return field.title
    return super(self.__class__, self).__doc__


FieldProperty.__doc__ = property(get_field_doc)


def includeme(config):
    """pyams_utils features include"""
    from .include import include_package  # pylint: disable=import-outside-toplevel
    include_package(config)
