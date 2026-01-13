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

"""PyAMS_layer.vocabulary module

This module provides vocabularies used to get skins lists.
"""

from zope.componentvocabulary.vocabulary import UtilityTerm, UtilityVocabulary

from pyams_layer.interfaces import BASE_SKINS_VOCABULARY_NAME, IPyAMSUserLayer, ISkin, \
    USER_SKINS_VOCABULARY_NAME
from pyams_utils.request import check_request
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'


@vocabulary_config(name=BASE_SKINS_VOCABULARY_NAME)
class SkinsVocabulary(UtilityVocabulary):
    """PyAMS skins vocabulary"""

    interface = ISkin
    nameOnly = True

    def __init__(self, context=None, **kw):
        # pylint: disable=super-init-not-called,unused-argument
        request = check_request()
        registry = request.registry
        translate = request.localizer.translate
        utils = [
            (name, translate(util.label))
            for (name, util) in registry.getUtilitiesFor(self.interface)
        ]
        self._terms = dict((title, UtilityTerm(name, title)) for name, title in utils)


@vocabulary_config(name=USER_SKINS_VOCABULARY_NAME)
class UserSkinsVocabulary(UtilityVocabulary):
    """PyAMS custom users skins vocabulary"""

    interface = ISkin
    nameOnly = True

    def __init__(self, context=None, **kw):
        # pylint: disable=super-init-not-called,unused-argument
        request = check_request()
        registry = request.registry
        translate = request.localizer.translate
        utils = [
            (name, translate(util.label))
            for (name, util) in registry.getUtilitiesFor(self.interface)
            if util.label and issubclass(util.layer, IPyAMSUserLayer)
        ]
        self._terms = dict((title, UtilityTerm(name, title)) for name, title in utils)
