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

"""PyAMS_layer.interfaces module

This module provides all layers and skins related interfaces.
"""

from pyramid.interfaces import IRequest
from zope.configuration.fields import GlobalInterface
from zope.interface import Attribute, Interface, implementer
from zope.interface.interfaces import IObjectEvent, ObjectEvent
from zope.schema import Bool, Choice, TextLine

from pyams_file.schema import FileField


__docformat__ = 'restructuredtext'

from pyams_layer import _


MANAGE_SKIN_PERMISSION = 'pyams.ManageSkin'
'''Permission required to manage rendering skin'''


class IResources(Interface):
    """Get list of CSS and Javascript resources associated with given context"""

    resources = Attribute("Resources to include")
    """Iterable of resources to include into page

    The best way to handle resources is to use Fanstatic to automatically
    include CSS and Javascript tags.
    """


PYAMS_BASE_SKIN_NAME = 'PyAMS base skin'


class IBaseLayer(IRequest):
    """Base layer marker interface"""


class IFormLayer(Interface):
    """Custom layer for forms management"""


class IPyAMSLayer(IBaseLayer, IFormLayer):
    """PyAMS default layer"""


class IPyAMSUserLayer(IPyAMSLayer):
    """PyAMS custom user layer

    This layer is the base for all custom skins.
    Any component should provide a look and feel for this layer.
    """


BASE_SKINS_VOCABULARY_NAME = 'pyams_layer.skins'
USER_SKINS_VOCABULARY_NAME = 'pyams_layer.skin.user'


class ISkin(Interface):
    """Skin interface

    Skins are registered as utilities implementing this interface
    and defining request layer as attribute.
    """

    label = TextLine(title="Skin name")

    layer = GlobalInterface(title="Request layer",
                            description="This interface will be used to tag request layer",
                            required=True)


class ISkinChangedEvent(IObjectEvent):
    """Skin changed event"""


@implementer(ISkinChangedEvent)
class SkinChangedEvent(ObjectEvent):
    """Request skin changed event"""


class ISkinnable(Interface):
    """Skinnable content interface"""

    can_inherit_skin = Attribute("Check if skin can be inherited")

    inherit_skin = Bool(title=_("Inherit parent skin?"),
                        description=_("Should we reuse parent skin?"),
                        required=True,
                        default=False)

    override_skin = Bool(title=_("Don't inherit parent skin?"),
                         description=_("Should we override parent skin?"),
                         required=True,
                         default=True)

    skin_parent = Attribute("Skin parent (local or inherited)")

    skin = Choice(title=_("Custom graphic theme"),
                  description=_("This theme will be used to handle graphic design (colors and "
                                "images)"),
                  vocabulary=USER_SKINS_VOCABULARY_NAME,
                  required=False)

    def get_skin(self, request=None):
        """Get skin matching this content"""

    container_class = TextLine(title=_("Container class"),
                               description=_("CSS class given to main page container element"),
                               required=False)

    custom_stylesheet = FileField(title=_("Custom stylesheet"),
                                  description=_("This custom stylesheet will be used to override "
                                                "selected theme styles"),
                                  required=False)

    editor_stylesheet = FileField(title=_("Editor stylesheet"),
                                  description=_("Styles defined into this stylesheet will be "
                                                "available into HTML editor"),
                                  required=False)

    custom_script = FileField(title=_("Custom script"),
                              description=_("This custom javascript file will be used to add "
                                            "dynamic features to selected theme"),
                              required=False)


class IUserSkinnable(ISkinnable):
    """User skinnable content interface"""
