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

"""PyAMS_catalog.events module

This module register events subscribers which are automatically used to index, reindex or
unindex a content during it's lifecycle when it is added, modified or removed.
"""

from hypatia.interfaces import ICatalog
from persistent import IPersistent
from pyramid.settings import asbool
from pyramid.events import subscriber
from zope.intid.interfaces import IIntIdRemovedEvent
from zope.lifecycleevent import IObjectAddedEvent, IObjectModifiedEvent

from pyams_catalog.interfaces import DISABLE_CATALOG_SETTINGS_KEY
from pyams_catalog.utils import index_object, reindex_object, unindex_object
from pyams_utils.registry import get_utilities_for, get_pyramid_registry


__docformat__ = 'restructuredtext'


@subscriber(IObjectAddedEvent, context_selector=IPersistent)
def handle_new_object(event):
    """Index new persistent object"""
    registry = get_pyramid_registry()
    if asbool(registry.settings.get(DISABLE_CATALOG_SETTINGS_KEY)):
        return
    for _, catalog in get_utilities_for(ICatalog):
        index_object(event.object, catalog, ignore_notyet=True)


@subscriber(IObjectModifiedEvent, context_selector=IPersistent)
def handle_modified_object(event):
    """Update catalog for modified persistent object"""
    registry = get_pyramid_registry()
    if asbool(registry.settings.get(DISABLE_CATALOG_SETTINGS_KEY)):
        return
    for _, catalog in get_utilities_for(ICatalog):
        reindex_object(event.object, catalog)


@subscriber(IIntIdRemovedEvent, context_selector=IPersistent)
def handle_removed_object(event):
    """Un-index removed persistent object

    Don't use IObjectRemovedEvent to avoid objects from being already unregistered
    from IIntId utility!!!
    """
    registry = get_pyramid_registry()
    if asbool(registry.settings.get(DISABLE_CATALOG_SETTINGS_KEY)):
        return
    for _, catalog in get_utilities_for(ICatalog):
        unindex_object(event.object, catalog)
