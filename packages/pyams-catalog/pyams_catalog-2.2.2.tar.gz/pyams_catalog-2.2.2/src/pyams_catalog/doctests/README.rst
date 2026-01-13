=====================
PyAMS_catalog package
=====================


Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_site import includeme as include_site
    >>> include_site(config)
    >>> from pyams_i18n import includeme as include_i18n
    >>> include_i18n(config)
    >>> from pyams_catalog import includeme as include_catalog
    >>> include_catalog(config)

NLTK library must first be initialized before using text indexes:

    >>> import nltk
    >>> from pyams_utils.context import capture_all
    >>> with capture_all(nltk.download, 'punkt') as (status1, log1, errors1):
    ...     pass
    >>> status1
    True
    >>> with capture_all(nltk.download, 'punkt_tab') as (status2, log2, errors2):
    ...     pass
    >>> status2
    True
    >>> with capture_all(nltk.download, 'snowball_data') as (status3, log3, errors3):
    ...     pass
    >>> status3
    True
    >>> with capture_all(nltk.download, 'stopwords') as (status4, log4, errors4):
    ...     pass
    >>> status4
    True


Site generations
----------------

PyAMS_catalog package provides a site generation utility which is automatically checking for
a persistent catalog utility into local site manager:

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...
    Upgrading PyAMS I18n to generation 1...
    Upgrading PyAMS catalog to generation 1...

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyramid.threadlocal import manager
    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))

    >>> 'Catalog' in app.getSiteManager()
    True

    >>> from hypatia.interfaces import ICatalog
    >>> from pyams_utils.registry import get_utility
    >>> catalog = get_utility(ICatalog)

    >>> from pyams_utils.interfaces import ICacheKeyValue
    >>> ICacheKeyValue(catalog)
    'catalog::[]'


We have a catalog, we can now create an index:

    >>> from pyams_catalog.testing import IContentInterface, MyContent

    >>> from pyams_catalog.index import FieldIndexWithInterface, DatetimeIndexWithInterface
    >>> from pyams_catalog.index import KeywordIndexWithInterface, FacetIndexWithInterface
    >>> from pyams_catalog.index import TextIndexWithInterface
    >>> from pyams_catalog.generations import check_required_indexes

    >>> REQUIRED_INDEXES = [('content.value', FieldIndexWithInterface,
    ...                      {'interface': IContentInterface, 'discriminator': 'value'}),
    ...                     ('content.first_date', DatetimeIndexWithInterface,
    ...                      {'interface': IContentInterface, 'discriminator': 'first_date'}),
    ...                     ('content.keyword', KeywordIndexWithInterface,
    ...                      {'interface': IContentInterface, 'discriminator': 'keywords'}),
    ...                     ('content.facet', FacetIndexWithInterface,
    ...                      {'interface': IContentInterface, 'discriminator': 'facets',
    ...                       'facets': ['category', 'price']}),
    ...                     ('content.text', TextIndexWithInterface,
    ...                      {'interface': IContentInterface, 'discriminator': 'text'}),
    ...                     ('content.empty', FieldIndexWithInterface,
    ...                      {'interface': IContentInterface, 'discriminator': 'empty'})]
    >>> check_required_indexes(app, REQUIRED_INDEXES)
    >>> 'content.value' in catalog
    True
    >>> value_index = catalog['content.value']
    >>> list(value_index.unique_values())
    []
    >>> date_index = catalog['content.first_date']
    >>> keyword_index = catalog['content.keyword']
    >>> facet_index = catalog['content.facet']
    >>> text_index = catalog['content.text']

    >>> ICacheKeyValue(catalog)
    "catalog::['content.empty', 'content.facet', 'content.first_date', 'content.keyword', 'content.text', 'content.value']"


Indexing contents
-----------------

The index is created, we can now create and index contents:

    >>> from datetime import datetime

    >>> content = MyContent()
    >>> content.value = 'Test value'
    >>> content.first_date = datetime.utcnow()
    >>> content.text = "This is a long text"

    >>> from zope.lifecycleevent import ObjectAddedEvent, ObjectModifiedEvent, ObjectRemovedEvent
    >>> app['content1'] = content
    >>> config.registry.notify(ObjectAddedEvent(content, app))
    >>> list(value_index.unique_values())
    ['Test value']
    >>> list(date_index.unique_values())
    [datetime.datetime(..., ..., ..., 0, 0)]
    >>> list(keyword_index.unique_values())
    ['category1', 'category2']
    >>> list(facet_index.unique_values())
    ['category', 'price']
    >>> text_index.word_count()
    4

If we try to index another object which doesn't implement index interface, the index is not updated
even if the object provides the same attribute:

    >>> from pyams_catalog.testing import MyOtherContent
    >>> content2 = MyOtherContent()
    >>> app['content2'] = content2
    >>> config.registry.notify(ObjectAddedEvent(content2, app))
    >>> list(value_index.unique_values())
    ['Test value']


Using NLTK stemmers
-------------------

Full-text indexing relies on NLTK package processors; there is a simple fulltext processor, and
a stemmed processor using a Snowball algorithm:

    >>> from pyams_catalog.nltk import NltkStemmedTextProcessor
    >>> processor = NltkStemmedTextProcessor('en')
    >>> processor.process(("This is a text sample for tests",))
    ['text', 'sampl', 'test']
    >>> processor.processGlob(("This is a text* sample* with globals for tests",))
    ['text', 'sampl', 'global', 'test']

    >>> from pyams_catalog.nltk import NltkFullTextProcessor
    >>> processor = NltkFullTextProcessor('en')
    >>> processor.process(("This is a text sample for tests",))
    ['this*', 'is*', 'text*', 'sample*', 'for*', 'tests*']
    >>> processor.processGlob(("This is a text* sample* with globals for tests",))
    ['this*', 'is*', 'text*', 'sample*', 'with*', 'globals*', 'for*', 'tests*']


Catalog queries
---------------

We have to be able to query catalog contents; the CatalogResultSet is a wrapper around an
Hypatia query which iterates over database objects instead of internal IDs references:

    >>> from hypatia.catalog import CatalogQuery
    >>> from hypatia.query import Query, Eq
    >>> from pyams_catalog.query import ResultSet, CatalogResultSet

    >>> params = Eq(value_index, 'Test value')
    >>> result = next(iter(ResultSet(CatalogQuery(catalog).query(params))))
    >>> result is content
    True

PyAMS_catalog provides a few features, to be able to insert elements before or after the
initial results set:

    >>> result = CatalogResultSet(CatalogQuery(catalog).query(params))
    >>> result.prepend(('first1', 'first2'))
    >>> result.append(('last1', 'last2'))
    >>> list(result)
    ['first1', 'first2', <pyams_catalog.testing.MyContent object at 0x...>, 'last1', 'last2']

It's also possible to combine several queries with an "or" or an "and"; it's not really different
from Hypatia boolean operators, but it allows to combine a query with a null object:

    >>> from pyams_catalog.query import or_, and_

    >>> query1 = params
    >>> query2 = or_(None, query1)
    >>> query2
    <hypatia.query.Eq object at 0x...>

    >>> query2 is query1
    True
    >>> query2 = and_(None, query1)
    >>> query2
    <hypatia.query.Eq object at 0x...>
    >>> query2 is query1
    True

    >>> query2 = params
    >>> query3 = or_(query1, query2)
    >>> query3
    <hypatia.query.Or object at 0x...>
    >>> query3 is query1
    False
    >>> query3 is query2
    False
    >>> query3 = and_(query1, query2)
    >>> query3
    <hypatia.query.And object at 0x...>
    >>> query3 is query1
    False
    >>> query3 is query2
    False


Updating contents
-----------------

    >>> content.value = 'Modified value'
    >>> config.registry.notify(ObjectModifiedEvent(content))
    >>> params = Eq(value_index, 'Modified value')
    >>> result = next(iter(CatalogResultSet(CatalogQuery(catalog).query(params))))
    >>> result is content
    True
    >>> list(value_index.unique_values())
    ['Modified value']


I18n text indexes
-----------------

PyAMS_catalog allows to define special indexes to handle I18n attributes as defined into PyAMS_i18n
packages; you have to create a dedicated index for each language:

    >>> from hypatia.text.lexicon import Lexicon
    >>> from pyams_catalog.nltk import NltkFullTextProcessor, get_fulltext_lexicon
    >>> from pyams_catalog.testing import II18nContentInterface

    >>> from pyams_catalog.i18n import I18nTextIndexWithInterface
    >>> REQUIRED_INDEXES = [('content.i18n:en', I18nTextIndexWithInterface,
    ...                      {'language': 'en',
    ...                       'interface': II18nContentInterface,
    ...                       'discriminator': 'i18n_value',
    ...                       'lexicon': lambda: get_fulltext_lexicon('english')}), ]
    >>> check_required_indexes(app, REQUIRED_INDEXES)
    >>> 'content.i18n:en' in catalog
    True
    >>> i18n_index = catalog['content.i18n:en']
    >>> i18n_index.word_count()
    0

    >>> from pyams_catalog.testing import I18nContent

    >>> i18n_content = I18nContent()
    >>> i18n_content.i18n_value = {'en': 'I18n text values'}
    >>> app['i18n_content'] = i18n_content
    >>> config.registry.notify(ObjectAddedEvent(i18n_content, app))
    >>> i18n_index.word_count()
    3

    >>> from hypatia.query import Contains
    >>> params = Contains(i18n_index, 'text OR value')
    >>> result = next(iter(CatalogResultSet(CatalogQuery(catalog).query(params))))
    >>> result
    <pyams_catalog.testing.I18nContent object at 0x...>
    >>> result is i18n_content
    True

Only exact words queries are supported with a text index using a fulltext processor; you need a
stemmed processor for this to work:

    >>> params = Contains(i18n_index, 'test AND value')
    >>> result = next(iter(CatalogResultSet(CatalogQuery(catalog).query(params))))
    Traceback (most recent call last):
    ...
    StopIteration

So let's create a text index with a stemmed lexicon:

    >>> from pyams_catalog.nltk import NltkStemmedTextProcessor

    >>> def get_stemmed_lexicon(language):
    ...     return Lexicon(NltkStemmedTextProcessor(language=language))

    >>> from pyams_catalog.i18n import I18nTextIndexWithInterface
    >>> REQUIRED_INDEXES = [('content.i18n.stemmed:en', I18nTextIndexWithInterface,
    ...                      {'language': 'en',
    ...                       'interface': II18nContentInterface,
    ...                       'discriminator': 'i18n_value',
    ...                       'lexicon': lambda: get_stemmed_lexicon('english')}), ]
    >>> check_required_indexes(app, REQUIRED_INDEXES)
    >>> 'content.i18n.stemmed:en' in catalog
    True
    >>> stem_index = catalog['content.i18n.stemmed:en']
    >>> stem_index.word_count()
    0
    >>> config.registry.notify(ObjectModifiedEvent(i18n_content, app))
    >>> stem_index.word_count()
    3

    >>> params = Contains(stem_index, 'text AND value')
    >>> result = next(iter(CatalogResultSet(CatalogQuery(catalog).query(params))))
    >>> result is i18n_content
    True

We can also create a query filter based on null, empty or unindexed values. But keep in mind that only contents
which implement index interface are returned by "IsNone" operator:

    >>> from pyams_catalog.query import IsNone

    >>> empty_index = catalog['content.empty']

    >>> params = IsNone(empty_index)
    >>> result = list(CatalogResultSet(CatalogQuery(catalog).query(params)))
    >>> empty_index.interface.providedBy(content)
    True
    >>> len(result)
    1
    >>> content in result
    True

    >>> params = IsNone(keyword_index)
    >>> result = list(CatalogResultSet(CatalogQuery(catalog).query(params)))
    >>> keyword_index.interface.providedBy(content2)
    False
    >>> len(result)
    0
    >>> getattr(content2, 'keywords', None) is None
    True
    >>> content2 in result
    False


Deleting contents
-----------------

Let's now delete these indexed contents:

    >>> del app['content1']
    >>> config.registry.notify(ObjectRemovedEvent(content, app))
    >>> list(value_index.unique_values())
    []

    >>> del app['i18n_content']
    >>> config.registry.notify(ObjectRemovedEvent(i18n_content, app))
    >>> i18n_index.word_count()
    0


Reindexing database contents
----------------------------

It is always possible to reindex all database contents into the catalog; this feature is used
by the *pyams_index* command line script:

    >>> from pyams_catalog.utils import index_site
    >>> request = DummyRequest(context=app)
    >>> index_site(request, autocommit=False)
             1: Indexing <pyams_site.site.BaseSiteRoot object at 0x... oid 0x1 in <ZODB.Connection.Connection object at 0x...>>
    <pyams_site.site.BaseSiteRoot object at 0x... oid 0x1 in <ZODB.Connection.Connection object at 0x...>>

    >>> from pyams_utils.context import capture_all
    >>> from pyams_catalog.scripts import pyams_index_cmd
    >>> with capture_all(pyams_index_cmd) as (result, output, errors):
    ...     pass
    Traceback (most recent call last):
    ...
    SystemExit: 2


Tests cleanup:

    >>> tearDown()
