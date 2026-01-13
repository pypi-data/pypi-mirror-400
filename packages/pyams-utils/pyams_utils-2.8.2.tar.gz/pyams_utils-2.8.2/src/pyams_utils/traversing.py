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

"""PyAMS_utils.traversing module

This module provides a custom Pyramid "namespace" traverser: using "++name++" URLs allows
to traverse URLs based on custom traversing adapters.

It also provides a "get_parent" function, which returns a parent object of given object providing
a given interface.
"""

from pyramid.exceptions import NotFound, URLDecodeError
from pyramid.interfaces import VH_ROOT_KEY
from pyramid.location import lineage
from pyramid.traversal import ResourceTreeTraverser, split_path_info, decode_path_info
from pyramid.util import is_nonstr_iter
from zope.component import queryAdapter, queryMultiAdapter
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.location import ILocation
from zope.location.interfaces import IContained
from zope.traversing.interfaces import BeforeTraverseEvent, ITraversable

from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.interfaces.traversing import IPathElements
from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'


class NamespaceTraverser(ResourceTreeTraverser):
    """Custom traverser handling views and namespaces

    This is an upgraded version of native Pyramid traverser.
    It adds:
    - a new BeforeTraverseEvent before traversing each object in the path
    - support for namespaces with "++" notation
    """

    PLUS_SELECTOR = '+'
    NAMESPACE_SELECTOR = PLUS_SELECTOR * 2

    def __call__(self, request):
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        environ = request.environ
        matchdict = request.matchdict

        if matchdict is not None:
            path = matchdict.get('traverse', '/') or '/'
            if is_nonstr_iter(path):
                # this is a *traverse stararg (not a {traverse})
                # routing has already decoded these elements, so we just
                # need to join them
                path = '/' + '/'.join(path) or '/'

            subpath = matchdict.get('subpath', ())
            if not is_nonstr_iter(subpath):
                # this is not a *subpath stararg (just a {subpath})
                # routing has already decoded this string, so we just need
                # to split it
                subpath = split_path_info(subpath)

        else:
            subpath = ()
            try:
                # empty if mounted under a path in mod_wsgi, for example
                path = request.path_info or '/'
            except KeyError:
                # if environ['PATH_INFO'] is just not there
                path = '/'
            except UnicodeDecodeError as exc:
                raise URLDecodeError(exc.encoding, exc.object, exc.start, exc.end, exc.reason) \
                    from exc

        if VH_ROOT_KEY in environ:
            # HTTP_X_VHM_ROOT
            vroot_path = decode_path_info(environ[VH_ROOT_KEY])
            vroot_tuple = split_path_info(vroot_path)
            vpath = vroot_path + path
            vroot_idx = len(vroot_tuple) - 1
        else:
            vroot_tuple = ()
            vpath = path
            vroot_idx = -1

        root = self.root
        obj = vroot = root

        request.registry.notify(BeforeTraverseEvent(root, request))

        if vpath == '/':
            # invariant: vpath must not be empty
            # prevent a call to traversal_path if we know it's going
            # to return the empty tuple
            vpath_tuple = ()

        else:
            # we do dead reckoning here via tuple slicing instead of
            # pushing and popping temporary lists for speed purposes
            # and this hurts readability; apologies
            i = 0
            plus_selector = self.PLUS_SELECTOR
            ns_selector = self.NAMESPACE_SELECTOR
            view_selector = self.VIEW_SELECTOR
            vpath_tuple = split_path_info(vpath)

            for segment in vpath_tuple:
                if obj is not root:
                    request.registry.notify(BeforeTraverseEvent(obj, request))

                if segment == plus_selector:
                    # check for custom namespace called '+'
                    # currently this namespace is used in PyAMS_default_theme package to get
                    # direct access to a given content
                    traverser = queryMultiAdapter((obj, request), ITraversable, '+')
                    if traverser is None:
                        raise NotFound()
                    try:
                        obj = traverser.traverse(vpath_tuple[vroot_idx + i + 2],
                                                 vpath_tuple[vroot_idx + i + 3:])
                    except IndexError as exc:
                        # the "+" namespace traverser is waiting for additional elements from
                        # input URL so a "+" URL not followed by something else is just an error!
                        raise NotFound() from exc
                    else:
                        i += 1
                        return {
                            'context': obj,
                            'view_name': ''.join(vpath_tuple[vroot_idx + i + 2:]),
                            'subpath': vpath_tuple[i + 2:],
                            'traversed': vpath_tuple[:vroot_idx + i + 2],
                            'virtual_root': vroot,
                            'virtual_root_path': vroot_tuple,
                            'root': root
                        }

                elif segment[:2] == ns_selector:
                    # check for namespace prefixed by '++'
                    # when a namespace is detected, named "ITraversable" multi-adapters are
                    # searched for context and request, or for context, sequentially; a NotFound
                    # exception is raised if traverser can't be found, otherwise it's "traverse"
                    # method is called to get new context
                    nss, name = segment[2:].split(ns_selector, 1)
                    traverser = queryMultiAdapter((obj, request), ITraversable, nss)
                    if traverser is None:
                        traverser = queryAdapter(obj, ITraversable, nss)
                    if traverser is None:
                        raise NotFound()
                    obj = traverser.traverse(name, vpath_tuple[vroot_idx + i + 1:])
                    i += 1
                    continue

                elif segment[:2] == view_selector:
                    # check for view name prefixed by '@@'
                    return {
                        'context': obj,
                        'view_name': segment[2:],
                        'subpath': vpath_tuple[i + 1:],
                        'traversed': vpath_tuple[:vroot_idx + i + 1],
                        'virtual_root': vroot,
                        'virtual_root_path': vroot_tuple,
                        'root': root
                    }

                try:
                    getitem = obj.__getitem__
                except AttributeError:
                    return {
                        'context': obj,
                        'view_name': segment,
                        'subpath': vpath_tuple[i + 1:],
                        'traversed': vpath_tuple[:vroot_idx + i + 1],
                        'virtual_root': vroot,
                        'virtual_root_path': vroot_tuple,
                        'root': root
                    }

                try:
                    next_item = getitem(segment)
                except KeyError:
                    return {
                        'context': obj,
                        'view_name': segment,
                        'subpath': vpath_tuple[i + 1:],
                        'traversed': vpath_tuple[:vroot_idx + i + 1],
                        'virtual_root': vroot,
                        'virtual_root_path': vroot_tuple,
                        'root': root
                    }
                if i == vroot_idx:
                    vroot = next_item
                obj = next_item
                i += 1

        if obj is not root:
            request.registry.notify(BeforeTraverseEvent(obj, request))

        return {
            'context': obj,
            'view_name': '',
            'subpath': subpath,
            'traversed': vpath_tuple,
            'virtual_root': vroot,
            'virtual_root_path': vroot_tuple,
            'root': root
        }


def get_name(context):
    """Get context name"""
    return ILocation(context).__name__


def get_parent(context, interface=Interface, allow_context=True, condition=None):
    """Get first parent of the context that implements given interface

    :param object context: base element
    :param Interface interface: the interface that parend should implement
    :param boolean allow_context: if 'True' (the default), traversing is done starting with
        context; otherwise, traversing is done starting from context's parent
    :param callable condition: an optional function that should return a 'True' result when
        called with parent as first argument
    :return:
    """
    if allow_context:
        parent = context
    else:
        parent = getattr(context, '__parent__', None)
    for context in lineage(parent):
        if interface.providedBy(context) and ((not condition) or condition(context)):
            return context
    return None


def get_parents_until(context, interface=Interface, allow_context=True, condition=None):
    """Get iterator over context parents until a parent with provided interface

    :param object context: base element
    :param Interface interface: the interface that ending parent should implement
    :param boolean allow_context: if 'True' (the default), traversing is done starting with
        context; otherwise, traversing is done starting from context's parent
    :param callable condition: an optional function which is called on each parent element
        and which should return a 'True' result for parent to be yielded by iterator
    :return: an iterator over context's parents
    """
    if allow_context:
        parent = context
    else:
        parent = getattr(context, '__parent__', None)
    for context in lineage(parent):
        yield context
        if interface.providedBy(context) and ((not condition) or condition(context)):
            return


@adapter_config(required=IContained, provides=IPathElements)
class PathElementsAdapter(ContextAdapter):
    """Contained object path elements adapter

    This interface is intended to be used inside a keyword index to
    be able to search object based on a given parent
    """

    @property
    def parents(self):
        """Get list of parents OIDs"""
        intids = query_utility(IIntIds)
        if intids is None:
            return []
        return [intids.register(parent) for parent in lineage(self.context)]
