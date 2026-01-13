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

"""PyAMS_catalog.utils module

This module defines several utility functions which are used to update catalog.
"""

import logging

import transaction
from ZODB.interfaces import IBroken
from hypatia.interfaces import ICatalog
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.keyreference.interfaces import NotYet

from pyams_catalog.interfaces import BeforeObjectIndexEvent, INoAutoIndex
from pyams_site.site import site_factory
from pyams_utils.adapter import adapter_config
from pyams_utils.finder import find_objects_providing
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.registry import get_pyramid_registry, get_utility, query_utility, \
    set_local_registry

__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (catalog)')


@adapter_config(required=ICatalog,
                provides=ICacheKeyValue)
def catalog_key_adapter(obj):
    """Catalog key value adapter"""
    return 'catalog::{}'.format(str(sorted(obj)))


def index_object(obj, catalog='', ignore_notyet=False):
    """Index given object into catalog"""
    LOGGER.debug(f"Indexing object {obj!r}")
    intids = query_utility(IIntIds)
    if intids is not None:
        try:
            object_id = intids.register(obj)
        except NotYet:
            if not ignore_notyet:
                raise
        else:
            if isinstance(catalog, str):
                catalog = query_utility(ICatalog, name=catalog)
            if catalog is not None:
                get_pyramid_registry().notify(BeforeObjectIndexEvent(obj))
                catalog.index_doc(object_id, obj)


def reindex_object(obj, catalog=''):
    """Reindex given object into catalog"""
    LOGGER.debug(f"Re-indexing object {obj!r}")
    intids = query_utility(IIntIds)
    if intids is not None:
        object_id = intids.queryId(obj)
        if object_id is not None:
            if isinstance(catalog, str):
                catalog = query_utility(ICatalog, name=catalog)
            if catalog is not None:
                get_pyramid_registry().notify(BeforeObjectIndexEvent(obj))
                catalog.reindex_doc(object_id, obj)


def unindex_object(obj, catalog=''):
    """Un-index given object from catalog"""
    LOGGER.debug(f"Un-indexing object {obj!r}")
    intids = query_utility(IIntIds)
    if intids is not None:
        object_id = intids.queryId(obj)
        if object_id is not None:
            if isinstance(catalog, str):
                catalog = query_utility(ICatalog, name=catalog)
            if catalog is not None:
                catalog.unindex_doc(object_id)


def index_site(request, autocommit=True):
    """Index all site contents in internal catalog"""
    application = site_factory(request)
    if application is not None:
        try:
            set_local_registry(application.getSiteManager())
            catalog = get_utility(ICatalog)
            catalog.reset()
            transaction.savepoint()
            intids = get_utility(IIntIds)
            for index, document in enumerate(find_objects_providing(application, Interface)):
                if INoAutoIndex.providedBy(document):
                    continue
                if IBroken.providedBy(document):
                    print(f"Skipping broken object: {document!r}")
                else:
                    print(f"{index+1:10}: Indexing {document!r}")
                    catalog.reindex_doc(intids.register(document), document)
                    if not index % 100:
                        transaction.savepoint()
        finally:
            set_local_registry(None)
        if autocommit:
            transaction.commit()
    return application
