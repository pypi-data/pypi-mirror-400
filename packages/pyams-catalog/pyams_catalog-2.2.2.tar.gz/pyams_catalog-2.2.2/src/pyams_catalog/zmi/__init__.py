#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_catalog.zmi main module

"""

from hypatia.interfaces import ICatalog
from zope.interface import Interface

from pyams_utils.adapter import adapter_config
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel

__docformat__ = 'restructuredtext'

from pyams_catalog import _  # pylint: ungrouped-imports


@adapter_config(required=(ICatalog, IAdminLayer, Interface),
                provides=IObjectLabel)
def catalog_label(context, request, view):
    """Catalog label getter"""
    return request.localizer.translate(_("Catalog"))
