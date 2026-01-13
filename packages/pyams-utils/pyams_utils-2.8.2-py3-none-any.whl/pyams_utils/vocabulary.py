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

"""PyAMS_utils.vocabulary module

This module is used to handle vocabularies.
"""

import logging

import venusian
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary, getVocabularyRegistry

from pyams_utils.registry import get_utilities_for, get_utility


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (utils)')


class LocalUtilitiesVocabulary(SimpleVocabulary):
    """Local utilities vocabulary"""

    interface = None
    title_factory = None

    def __init__(self, context=None):  # pylint: disable=unused-argument
        if self.title_factory is None:
            factory = self.get_title
        else:
            factory = self.title_factory
        terms = sorted([
            SimpleTerm(name, title=factory(util))
            for name, util in get_utilities_for(self.interface)
        ], key=lambda x: x.title)
        super().__init__(terms)

    @staticmethod
    def get_title(util):
        """Utility title getter"""
        return util.name or ''

    def get_utility(self, value):
        """Get utility matching provided value"""
        return get_utility(self.interface, name=value)


class vocabulary_config:  # pylint: disable=invalid-name
    """Class decorator to define a vocabulary

    :param str name: name of the registered vocabulary

    This is, for example, how a vocabulary of registered ZEO connections utilities is created:

    .. code-block:: python

        from pyams_utils.interfaces.zeo import IZEOConnection

        from pyams_utils.registry import get_utilities_for
        from pyams_utils.vocabulary import vocabulary_config
        from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

        @vocabulary_config(name='PyAMS ZEO connections')
        class ZEOConnectionVocabulary(SimpleVocabulary):
            '''ZEO connections vocabulary'''

            def __init__(self, context=None):
                terms = [SimpleTerm(name, title=util.name)
                         for name, util in get_utilities_for(IZEOConnection)]
                super(ZEOConnectionVocabulary, self).__init__(terms)

    You can then use such a vocabulary in any schema field:

    .. code-block:: python

        from zope.interface import Interface
        from zope.schema import Choice

        class MySchema(Interface):
            '''Custom schema interface'''

            zeo_connection_name = Choice(title='ZEO connection name',
                                         description='Please select a registered ZEO connection',
                                         vocabulary='PyAMS ZEO connections',
                                         required=False)
    """

    venusian = venusian

    def __init__(self, name, **settings):
        self.name = name
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, obj):  # pylint: disable=unused-argument
            LOGGER.debug(f'Registering class {obj!s} as vocabulary with name "{self.name}"')
            directlyProvides(obj, IVocabularyFactory)
            getVocabularyRegistry().register(self.name, obj)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)

        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped
