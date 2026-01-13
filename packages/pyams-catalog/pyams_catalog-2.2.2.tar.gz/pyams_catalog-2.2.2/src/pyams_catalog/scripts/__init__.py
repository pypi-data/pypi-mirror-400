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

"""PyAMS_catalog.scripts module

This module provides a command line script which can be used to reindex a whole database
content.

The script iterates all database contents using the
:py:class:`zope.location.interfaces.ISublocations` interface.
"""

import argparse
import sys
import textwrap

from pyramid.paster import bootstrap

from pyams_catalog.utils import index_site


__docformat__ = 'restructuredtext'


def pyams_index_cmd():
    """Index (or reindex) all contents into Hypatia catalog"""
    usage = "usage: {0} config_uri".format(sys.argv[0])
    description = """Update catalog with all database objects.
                  Usage: pyams_index production.ini
                  """
    parser = argparse.ArgumentParser(usage=usage,
                                     description=textwrap.dedent(description))
    parser.add_argument('config_uri', help='Name of configuration file')
    args = parser.parse_args()

    config_uri = args.config_uri
    env = bootstrap(config_uri)
    closer = env['closer']
    try:
        index_site(env['request'])
    finally:
        closer()
