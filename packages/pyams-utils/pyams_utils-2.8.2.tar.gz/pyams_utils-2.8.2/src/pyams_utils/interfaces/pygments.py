#
# Copyright (c) 2008-2018 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.interfaces.pygments module

This module is used to load Pygments CSS
"""

from zope.interface import Interface
from zope.schema import Bool, Choice


__docformat__ = 'restructuredtext'

from pyams_utils import _


PYGMENTS_LEXERS_VOCABULARY_NAME = 'pyams_utils.pygments.lexers'
PYGMENTS_STYLES_VOCABULARY_NAME = 'pyams_utils.pygments.styles'


class IPygmentsCodeConfiguration(Interface):
    """Pygments html formatter options"""

    lexer = Choice(title=_("Selected lexer"),
                   description=_("Lexer used to format source code"),
                   required=True,
                   vocabulary=PYGMENTS_LEXERS_VOCABULARY_NAME,
                   default='auto')

    display_linenos = Bool(title=_("Display line numbers?"),
                           description=_("If 'no', line numbers will be hidden"),
                           required=True,
                           default=True)

    disable_wrap = Bool(title=_("Lines wrap?"),
                        description=_("If 'yes', lines wraps will be enabled; line numbers will "
                                      "not be displayed if lines wrap is enabled..."),
                        required=True,
                        default=False)

    style = Choice(title=_("Color style"),
                   description=_("Selected color style"),
                   required=True,
                   vocabulary=PYGMENTS_STYLES_VOCABULARY_NAME,
                   default='default')
