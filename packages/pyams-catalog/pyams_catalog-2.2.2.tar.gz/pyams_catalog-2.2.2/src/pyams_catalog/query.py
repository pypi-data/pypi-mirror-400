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

"""PyAMS_catalog.query module
"""

from hypatia.query import Comparator, Query
from zope.intid.interfaces import IIntIds

from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'


class IsNone(Comparator):
    """Index query search for None values"""

    def __init__(self, index):
        super().__init__(index, None)

    def _apply(self, name):
        return self.index.not_indexed()


class ResultSet:
    """Base catalog query result set wrapper

    This class just wraps a query result to return final objects
    instead of internal IDs.
    """

    def __init__(self, query):
        self.query = query
        self.intids = query_utility(IIntIds)

    def __iter__(self):
        intids = self.intids
        if intids is not None:
            query = self.query
            if isinstance(query, Query):
                query = query.execute()
            if isinstance(query, tuple):
                query = query[1]
            for oid in query:
                yield intids.queryObject(oid)


class CatalogResultSet:
    """Catalog query result set wrapper"""

    def __init__(self, query):
        self.query = query
        self.intids = query_utility(IIntIds)
        self.first = []
        self.last = []

    def __iter__(self):
        for item in self.first:
            yield item
        intids = self.intids
        if intids is not None:
            query = self.query
            if isinstance(query, Query):
                query = query.execute()
            if isinstance(query, tuple):
                query = query[1]
            for oid in query:
                if isinstance(oid, int):
                    target = intids.queryObject(oid)
                    if target is not None:
                        yield target
                else:
                    yield oid
        for item in self.last:
            yield item

    def __len__(self):
        if isinstance(self.query, (list, tuple, ResultSet)):
            nb_docs = len(self.query)
        else:
            nb_docs = self.query[0]
        return len(self.first) + nb_docs + len(self.last)

    def prepend(self, items):
        """Insert a list of elements at the beginning of the results set"""
        insert = self.first.insert
        for index, item in enumerate(items):
            insert(index, item)

    def append(self, items):
        """Append a list of elements at the end of the results set"""
        append = self.last.append
        for item in items:
            append(item)


def or_(source, added):
    """Combine two queries with 'or'"""
    if source is None:
        source = added
    else:
        source |= added
    return source


def and_(source, added):
    """Combine two queries with 'and'"""
    if source is None:
        source = added
    else:
        source &= added
    return source
