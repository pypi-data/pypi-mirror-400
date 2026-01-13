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

"""PyAMS_catalog.generations main module

This module is checking for registered utilities on site upgrade, and provides functions which
can be used by generations utilities to check for missing indexes.
"""

import logging

from hypatia.catalog import Catalog
from hypatia.interfaces import ICatalog
from zope.interface.interface import InterfaceClass
from zope.intid import IIntIds, IntIds

from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'

LOGGER = logging.getLogger('PyAMS (catalog)')

RENAMED_CLASSES = {
    'pyams_i18n.index I18nTextIndexMixin': 'pyams_catalog.i18n I18nTextIndexMixin',
    'pyams_i18n.index I18nTextIndexWithInterface': 'pyams_catalog.i18n I18nTextIndexWithInterface'
}

REQUIRED_UTILITIES = ((IIntIds, '', IntIds, 'Internal IDs'),
                      (ICatalog, '', Catalog, 'Catalog'),)


@utility_config(name='PyAMS catalog', provides=ISiteGenerations)
class CatalogGenerationsChecker:
    """Catalog generations checker"""

    order = 30
    generation = 1

    def evolve(self, site, current=None):  # pylint: disable=no-self-use,unused-argument
        """Check for required utilities"""
        check_required_utilities(site, REQUIRED_UTILITIES)


def check_required_indexes(site, indexes, catalog_name=''):
    """Utility function to check for required catalog indexes

    utilities argument is a tuple made of:
    - the index name
    - the index class
    - index factory arguments
    """
    sm = site.getSiteManager()  # pylint: disable=invalid-name
    catalog = sm.queryUtility(ICatalog, name=catalog_name)
    if catalog is None:
        LOGGER.warning("No catalog found! Index check ignored...")
        return
    for name, klass, args in indexes:
        index = catalog.get(name)
        if index is None:
            for key, value in args.copy().items():
                if callable(value) and not isinstance(value, InterfaceClass):
                    args[key] = value()
            index = klass(**args)
            catalog[name] = index
