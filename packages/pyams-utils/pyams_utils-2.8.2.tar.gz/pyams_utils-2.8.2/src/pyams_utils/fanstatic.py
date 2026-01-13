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

"""PyAMS_utils.fanstatic module

This module is a helper module to handle Fanstatic resources.

It includes several TALES extensions which can be used to include resources from a Chameleon
template, or to get path of a given resources from a template.
"""

import fanstatic
from fanstatic import Resource
from fanstatic.core import NeededResources, render_css, set_resource_file_existence_checking
from fanstatic.injector import TopBottomInjector
from pyramid.interfaces import IResponse
from pyramid.path import DottedNameResolver
from pyramid.threadlocal import RequestContext
from pyramid_fanstatic import fanstatic_config
from zope.interface import Interface

from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.data import format_data
from pyams_utils.interfaces.tales import ITALESExtension

__docformat__ = 'restructuredtext'


def render_js(url, defer=False):
    """Render tag to include Javascript resource"""
    return '<script type="text/javascript" src="%s"%s></script>' % \
           (url, ' defer' if defer else '')


class ResourceWithData(Resource):
    """Resource with data attributes

    Resource data is provided as a mapping, where "data-" prefix is not required.
    """

    data = None
    dependency_nr = 0

    def __init__(self, library, relpath, *args, **kwargs):
        if 'data' in kwargs:
            self.data = kwargs.pop('data')
        super().__init__(library, relpath,
                         renderer=self.custom_renderer,
                         *args, **kwargs)

    def get_data_str(self):
        """Get resource data as string"""
        return format_data(self.data)

    def custom_renderer(self, resource_url):
        """Custom resource renderer used to include custom data attributes"""
        if self.ext == '.js':
            result = render_js(resource_url)
        elif self.ext == '.css':
            result = render_css(resource_url)
        else:
            result = ''
        if self.data:
            result = result.replace(" type=",
                                    f" {self.get_data_str()} type=")
        return result


class ExternalResource(Resource):
    """Fanstatic external resource"""

    dependency_nr = 0

    def __init__(self, library, path, defer=False, resource_type=None, **kwargs):
        set_resource_file_existence_checking(False)
        try:
            if 'renderer' in kwargs:
                del kwargs['renderer']
            if 'bottom' not in kwargs:
                kwargs['bottom'] = path.endswith('.js')
            Resource.__init__(self, library, path, renderer=self.render, **kwargs)
        finally:
            set_resource_file_existence_checking(True)
        self.defer = defer
        if resource_type:
            self.resource_type = resource_type
        else:
            self.resource_type = path.rsplit('.', 1)[1].lower()

    def render(self, library_url):
        """Render resource tag"""
        if self.resource_type == 'css':
            return render_css(self.relpath)
        if self.resource_type == 'js':
            return render_js(self.relpath, self.defer)
        return ''


class IncludedResource(Resource):
    """Fanstatic included resource"""

    def render(self, library_url):
        """Render resource tag"""
        with open(self.fullpath(), 'r') as file:
            content = file.read()
            if self.ext == '.css':
                return f'<style>{content}</style>'
            if self.ext == '.js':
                return f'<script type="text/javascript">{content}</script>'
            return ''


def get_resource_path(resource, signature='--static--', versioning=True):
    """Get path for given resource"""
    if isinstance(resource, ExternalResource):
        return resource.relpath
    res = NeededResources(publisher_signature=signature, versioning=versioning)
    return f'{res.library_url(resource.library)}/{resource.relpath}'


@adapter_config(name='resource_path',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class FanstaticTalesExtension(ContextRequestViewAdapter):
    """tales:resource_path() TALES extension

    This TALES extension generates an URL matching a given Fanstatic resource.
    Resource is given as a string made of package name (in dotted form) followed by a colon and
    by the resource name.

    For example:

    .. code-block:: html

        <div tal:attributes="data-ams-plugin-pyams_content-src
                             extension:resource_path('pyams_content.zmi:pyams_content')" />
    """

    @staticmethod
    def render(resource):
        """TALES extension rendering method"""
        library, resource_name = resource.split(':')
        resolver = DottedNameResolver()
        module = resolver.maybe_resolve(library)
        resource = getattr(module, resource_name)
        return get_resource_path(resource)


@adapter_config(name='need_resource',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class FanstaticNeededResourceTalesExtension(ContextRequestViewAdapter):
    """tales:need_resource() TALES extension

    This extension generates a call to Fanstatic resource.need() function to include given resource
    into generated HTML code.
    Resource is given as a string made of package name (in dotted form) followed by a colon and by
    the resource name.

    For example:

    .. code-block:: html

        <tal:var define="tales:need_resource('pyams_content.zmi:pyams_content')" />
    """

    @staticmethod
    def render(resource):
        """TALES extension rendering method"""
        library, resource_name = resource.split(':')
        resolver = DottedNameResolver()
        module = resolver.maybe_resolve(library)
        resource = getattr(module, resource_name)
        resource.need()
        return ''


def inject_resources(request, registry, handler):
    """Inject Fanstatic resources into the given response"""
    settings = registry.settings.copy()
    config = fanstatic_config(settings)
    config.pop('use_application_uri', None)
    config.pop('injector', None)
    injector = TopBottomInjector(config)
    with RequestContext(request):
        try:
            needed = fanstatic.init_needed(**config)
            needed.set_base_url(request.application_url)
            request.environ[fanstatic.NEEDED] = needed
            response = handler() if callable(handler) else handler
            body = response.body if IResponse.providedBy(response) else response
            result = injector(body, needed, request, response)
        finally:
            fanstatic.del_needed()
    return result.decode() if isinstance(result, bytes) else result
