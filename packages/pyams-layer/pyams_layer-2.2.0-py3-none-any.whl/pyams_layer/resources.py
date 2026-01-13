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

"""PyAMS_layer.resources module

This module provides adapters and TALES extensions used to manage static resources
which are associated with skins.
"""

from datetime import datetime, timezone

from pyramid.interfaces import IRequest
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSUserLayer, IResources, ISkinnable
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config, get_adapter_weight
from pyams_utils.fanstatic import ExternalResource
from pyams_utils.interfaces.tales import ITALESExtension
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url


try:
    from myams_js import bootstrap, bootstrap_css
except ImportError:
    bootstrap = None


__docformat__ = 'restructuredtext'


@adapter_config(required=(Interface, IRequest, Interface),
                provides=IResources)
class DefaultResourcesAdapter(ContextRequestViewAdapter):
    """Default resources adapter"""

    @property
    def resources(self):
        """Resources getter"""
        if IPyAMSUserLayer.providedBy(self.request):
            return
        if bootstrap is not None:
            yield bootstrap_css
            yield bootstrap


@adapter_config(name='custom-skin',
                required=(Interface, IPyAMSUserLayer, Interface),
                provides=IResources)
class CustomSkinResourcesAdapter(ContextRequestViewAdapter):
    """Custom skin resources adapter"""

    weight = 999

    @property
    def resources(self):
        """Get custom skin resources"""
        request = self.request
        main_resources = request.registry.queryMultiAdapter(
            (self.context, request, self.view), IResources)
        if main_resources is None:
            return
        main_resource = main_resources.resources[-1]
        library = main_resource.library
        parent_resources = (main_resource,)
        skin_parent = get_parent(request.context, ISkinnable).skin_parent
        # include custom CSS files
        custom_css = skin_parent.custom_stylesheet  # pylint: disable=no-member
        if custom_css:
            dc = IZopeDublinCore(custom_css, None)  # pylint: disable=invalid-name
            modified = dc.modified if dc is not None else datetime.now(timezone.utc)
            # pylint: disable=no-member
            custom_css_url = absolute_url(custom_css, request,
                                          query={'_': modified.timestamp()})
            resource = library.known_resources.get(custom_css_url)
            if resource is None:
                resource = ExternalResource(library, custom_css_url, resource_type='css',
                                            depends=parent_resources)
            yield resource
        # include custom JS files
        custom_js = skin_parent.custom_script  # pylint: disable=no-member
        if custom_js:
            dc = IZopeDublinCore(custom_js, None)  # pylint: disable=invalid-name
            modified = dc.modified if dc is not None else datetime.now(timezone.utc)
            # pylint: disable=no-member
            custom_js_url = absolute_url(custom_js, request,
                                         query={'_': modified.timestamp()})
            resource = library.known_resources.get(custom_js_url)
            if resource is None:
                resource = ExternalResource(library, custom_js_url, resource_type='js',
                                            depends=parent_resources, bottom=True)
            yield resource


@adapter_config(name='resources',
                required=(Interface, IRequest, Interface),
                provides=ITALESExtension)
class ResourcesTalesExtension(ContextRequestViewAdapter):
    """tales:resources TALES extension"""

    def render(self, context=None):
        """Render Fanstatic resources"""
        if context is None:
            context = self.context
        for _name, adapter in sorted(
                self.request.registry.getAdapters((context, self.request, self.view),
                                                  IResources),
                key=get_adapter_weight):
            for resource in adapter.resources:
                resource.need()
        return ''
