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

"""PyAMS_utils.context module

This module provides a "context" selector which can be used as Pyramid's subscriber
predicate. Matching argument can be a class or an interface: for subscriber to be actually called,
subscriber's argument should inherit from it (if it's a class) or implement it (if it's an
interface).
"""

import sys
from contextlib import contextmanager
from io import StringIO


__docformat__ = 'restructuredtext'

from pyams_utils.factory import is_interface


@contextmanager
def capture(func, *args, **kwargs):
    """Context manager used to capture standard output"""
    out, sys.stdout = sys.stdout, StringIO()
    try:
        result = func(*args, **kwargs)
        sys.stdout.seek(0)
        yield result, sys.stdout.read()
    finally:
        sys.stdout = out


@contextmanager
def capture_stderr(func, *args, **kwargs):
    """Context manager used to capture error output"""
    err, sys.stderr = sys.stderr, StringIO()
    try:
        result = func(*args, **kwargs)
        sys.stderr.seek(0)
        yield result, sys.stderr.read()
    finally:
        sys.stderr = err


@contextmanager
def capture_all(func, *args, **kwargs):
    """Context manager used to capture standard output and standard error output"""
    out, sys.stdout, err, sys.stderr = sys.stdout, StringIO(), sys.stderr, StringIO()
    try:
        result = func(*args, **kwargs)
        sys.stdout.seek(0)
        sys.stderr.seek(0)
        yield result, sys.stdout.read(), sys.stderr.read()
    finally:
        sys.stdout, sys.stderr = out, err


class ContextSelector:  # pylint: disable=too-few-public-methods
    """Interface based context selector

    This selector can be used as a predicate to define a class or an interface that the context
    must inherit from or implement for the subscriber to be called:

    .. code-block:: python

        from zope.lifecycleevent.interfaces import IObjectModifiedEvent
        from pyams_site.interfaces import ISiteRoot

        @subscriber(IObjectModifiedEvent, context_selector=ISiteRoot)
        def siteroot_modified_event_handler(event):
            '''This is an event handler for an ISiteRoot object modification event'''
    """

    def __init__(self, ifaces, config):  # pylint: disable=unused-argument
        if not isinstance(ifaces, (list, tuple, set)):
            ifaces = (ifaces,)
        self.interfaces = ifaces

    def text(self):
        """Return selector """
        return 'context_selector = %s' % str(self.interfaces)

    phash = text

    def __call__(self, event):
        for intf in self.interfaces:
            if is_interface(intf):
                if hasattr(event, 'object') and intf.providedBy(event.object):
                    return True
                if hasattr(event, 'form') and intf.providedBy(event.form.context):
                    return True
            else:
                if hasattr(event, 'object') and isinstance(event.object, intf):
                    return True
                if hasattr(event, 'form') and isinstance(event.form.context, intf):
                    return True
        return False
