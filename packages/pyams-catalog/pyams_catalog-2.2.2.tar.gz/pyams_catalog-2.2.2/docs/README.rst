=====================
PyAMS_catalog package
=====================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_.


What is PyAMS_catalog?
======================

PyAMS_catalog is an extension package for PyAMS which provides features related to internal
Hypatia catalog management.

These features include custom indexes providing a discriminator based on interfaces support of
indexed contents, helpers based on NLTK library for fulltext indexing, and a few query tools.
