Changelog
=========

2.2.2
-----
 - updated query length getter
 - updated doctests and Gitlab-CI

2.2.1
-----
 - updated index script logging
 - added support for Python 3.12

2.2.0
-----
 - updated interfaces support in catalog indexes, so that objects which don't implement
   an index interface are not referenced anymore in the index; this can lead to different
   behaviour when using the IsNone comparator, as these objects are not referenced anymore
   in the "not indexed" part of the index!

2.1.0
-----
 - added index comparator to get null or un-indexed values

2.0.3
-----
 - updated catalog resultset length getter

2.0.2
-----
 - moved PyAMS_utils finder helper to new module

2.0.1
-----
 - updated buildout configuration

2.0.0
-----
 - migrated to Pyramid 2.0
 - added support for Python 3.10 and 3.11

1.3.2
-----
 - added fulltext lexicon creation helper

1.3.1
-----
 - updated NLTK text processor

1.3.0
-----
 - added catalog label adapter
 - updated package include scan

1.2.0
-----
 - fire IBeforeIndexEvent event before indexing objects into catalog

1.1.0
-----
 - removed support for Python < 3.7
 - added simple ResultSet class
 - updated doctests

1.0.7
-----
 - removed Travis-CI configuration

1.0.6
-----
 - updated "adapter_config" decorator argument name

1.0.5
-----
 - updated doctests due to changed NLTK base version

1.0.4
-----
 - updated doctests

1.0.3
-----
 - modified catalog cache key adapter
 - updated doctests

1.0.2
-----
 - added "autocommit" argument to "index_site" function, used for testing purposes
 - updated doctests

1.0.1
-----
 - updated Gitlab-CI tests and integration

1.0.0
-----
 - initial release
