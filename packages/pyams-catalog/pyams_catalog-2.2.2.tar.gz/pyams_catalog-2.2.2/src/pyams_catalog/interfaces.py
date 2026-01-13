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

"""PyAMS_catalog.interfaces module

This module provides all package interfaces.
"""

from zope.interface import Interface, implementer
from zope.interface.interfaces import IObjectEvent, ObjectEvent


DISABLE_CATALOG_SETTINGS_KEY = 'pyams_catalog.disable_indexing'

NLTK_LANGUAGES = {
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'fi': 'finnish',
    'fr': 'french',
    'de': 'german',
    'hu': 'hungarian',
    'it': 'italian',
    'no': 'norwegian',
    'po': 'porter',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'es': 'spanish',
    'sv': 'swedish'
}

NO_RESOLUTION = 6
SECOND_RESOLUTION = 5
MINUTE_RESOLUTION = 4
HOUR_RESOLUTION = 3
DATE_RESOLUTION = 2
MONTH_RESOLUTION = 1
YEAR_RESOLUTION = 0


class INoAutoIndex(Interface):
    """Marker interface for objects which shouldn't be automatically indexed"""


class IBeforeObjectIndexEvent(IObjectEvent):
    """Interface of event fired before object indexation

    This event can be useful to be able to initialize some attributes before object
    is registered into the catalog.
    """


@implementer(IBeforeObjectIndexEvent)
class BeforeObjectIndexEvent(ObjectEvent):
    """Event fired before object indexation"""
