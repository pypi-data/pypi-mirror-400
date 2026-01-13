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

"""PyAMS_layer.include module

This module is used for Pyramid integration
"""

from pyams_layer.interfaces import MANAGE_SKIN_PERMISSION
from pyams_layer.skin import UserSkinnableContentMixin, apply_skin, get_skin
from pyams_security.interfaces.names import SYSTEM_ADMIN_ROLE
from pyams_site.site import BaseSiteRoot


__docformat__ = 'restructuredtext'


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_layer:locales')

    # add request method
    config.add_request_method(apply_skin, 'apply_skin')
    config.add_request_method(get_skin, 'get_skin')

    # upgrade admin role
    config.upgrade_role(SYSTEM_ADMIN_ROLE,
                        permissions={
                            MANAGE_SKIN_PERMISSION
                        })

    # add skin support to site root
    if UserSkinnableContentMixin not in BaseSiteRoot.__bases__:
        BaseSiteRoot.__bases__ += (UserSkinnableContentMixin, )

    config.scan()
