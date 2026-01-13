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

"""PyAMS_catalog.index module

This module provides several Hypatia indexes which use a discriminator based on interface
support of indexes objects.

WARNING: objects which don't implement the requested interface are not referenced in the index, including
in the "not indexed" part.
"""

from datetime import date, datetime

from ZODB.broken import Broken
from hypatia.facet import FacetIndex
from hypatia.field import FieldIndex
from hypatia.keyword import KeywordIndex
from hypatia.text import TextIndex
from hypatia.text.lexicon import Lexicon
from hypatia.util import BaseIndexMixin
from persistent import Persistent

from pyams_catalog.interfaces import DATE_RESOLUTION, NO_RESOLUTION
from pyams_catalog.nltk import NltkFullTextProcessor

__docformat__ = 'restructuredtext'


_MARKER = object()


class InterfaceSupportIndexMixin(BaseIndexMixin):
    """Custom index mixin handling objects interfaces"""

    def __init__(self, interface):
        self.interface = interface

    def discriminate(self, obj, default):
        """See interface IIndexInjection"""
        if self.interface is not None:
            obj = self.interface(obj, None)
            if obj is None:
                return default

        if callable(self.discriminator):
            value = self.discriminator(obj, _MARKER)
        else:
            value = getattr(obj, self.discriminator, _MARKER)
            if callable(value):
                value = value(obj)

        if (value is None) or (value is _MARKER):
            return default

        if isinstance(value, Persistent):
            raise ValueError('Catalog cannot index persistent object {0!r}'.format(value))

        if isinstance(value, Broken):
            raise ValueError('Catalog cannot index broken object {0!r}'.format(value))

        return value
    
    def index_doc(self, docid, obj):
        """See interface IIndexInjection"""
        if self.interface is not None:
            obj = self.interface(obj, None)
            if obj is None:
                return None
        return super().index_doc(docid, obj)


class FieldIndexWithInterface(InterfaceSupportIndexMixin, FieldIndex):
    """Field index with interface support"""

    def __init__(self, interface, discriminator, family=None):
        InterfaceSupportIndexMixin.__init__(self, interface)
        FieldIndex.__init__(self, discriminator, family)


def get_resolution(value, resolution):
    """Set resolution of given date or datetime

        >>> from pyams_catalog.interfaces import *
        >>> from pyams_catalog.index import get_resolution
        >>> from datetime import date, datetime

        >>> get_resolution(None, YEAR_RESOLUTION) is None
        True
        >>> get_resolution('', DATE_RESOLUTION)
        ''

    Starting with dates:

        >>> today = date(2017, 7, 11)
        >>> get_resolution(today, YEAR_RESOLUTION)
        datetime.date(2017, 1, 1)
        >>> get_resolution(today, MONTH_RESOLUTION)
        datetime.date(2017, 7, 1)
        >>> get_resolution(today, DATE_RESOLUTION)
        datetime.date(2017, 7, 11)
        >>> get_resolution(today, NO_RESOLUTION) is None
        True

    Asking for a resolution higher than DATE with a date input only returns date:

        >>> get_resolution(today, MINUTE_RESOLUTION)
        datetime.date(2017, 7, 11)

    Same examples with datetimes:

        >>> now = datetime(2017, 7, 11, 13, 22, 10)
        >>> get_resolution(now, YEAR_RESOLUTION)
        datetime.datetime(2017, 1, 1, 0, 0)
        >>> get_resolution(now, MONTH_RESOLUTION)
        datetime.datetime(2017, 7, 1, 0, 0)
        >>> get_resolution(now, DATE_RESOLUTION)
        datetime.datetime(2017, 7, 11, 0, 0)
        >>> get_resolution(now, HOUR_RESOLUTION)
        datetime.datetime(2017, 7, 11, 13, 0)
        >>> get_resolution(now, MINUTE_RESOLUTION)
        datetime.datetime(2017, 7, 11, 13, 22)
        >>> get_resolution(now, SECOND_RESOLUTION)
        datetime.datetime(2017, 7, 11, 13, 22, 10)
        >>> get_resolution(now, NO_RESOLUTION) is None
        True
    """
    if not value:
        return value
    if resolution < NO_RESOLUTION:
        args = []
        if not isinstance(value, datetime):
            resolution = min(resolution, DATE_RESOLUTION)
        args.extend(value.timetuple()[:resolution+1])
        if isinstance(value, datetime):
            args.extend(([1] * (DATE_RESOLUTION - resolution) + [0] * 5)[:7-len(args)])
            args.append(value.tzinfo)
            value = datetime(*args)
        else:
            args.extend([1] * (DATE_RESOLUTION - resolution))
            value = date(*args)
        return value
    return None


class DatetimeIndexWithInterface(FieldIndexWithInterface):
    """Normalized datetime index with interface support"""

    def __init__(self, interface, discriminator, resolution=DATE_RESOLUTION, family=None):
        FieldIndexWithInterface.__init__(self, interface, discriminator, family)
        self.resolution = resolution

    def discriminate(self, obj, default):
        value = super().discriminate(obj, default)
        return get_resolution(value, self.resolution)


class KeywordIndexWithInterface(InterfaceSupportIndexMixin, KeywordIndex):
    """Keyword index with interface support"""

    def __init__(self, interface, discriminator, family=None):
        InterfaceSupportIndexMixin.__init__(self, interface)
        KeywordIndex.__init__(self, discriminator, family)


class FacetIndexWithInterface(InterfaceSupportIndexMixin, FacetIndex):
    """Facet index with interface support"""

    def __init__(self, interface, discriminator, facets, family=None):
        InterfaceSupportIndexMixin.__init__(self, interface)
        FacetIndex.__init__(self, discriminator, facets, family)


class TextIndexWithInterface(InterfaceSupportIndexMixin, TextIndex):
    """Text index with interface support"""

    # pylint: disable=too-many-arguments
    def __init__(self, interface, discriminator, lexicon=None, language='english',
                 index=None, family=None):
        InterfaceSupportIndexMixin.__init__(self, interface)
        if lexicon is None:
            lexicon = Lexicon(NltkFullTextProcessor(language))
        TextIndex.__init__(self, discriminator, lexicon, index, family)
