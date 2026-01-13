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

"""PyAMS_catalog.i18n module
"""

from ZODB.broken import Broken
from hypatia.text import TextIndex
from hypatia.text.lexicon import Lexicon
from hypatia.util import BaseIndexMixin
from persistent import Persistent

from pyams_catalog.nltk import NltkFullTextProcessor
from pyams_i18n.interfaces import II18n


__docformat__ = 'restructuredtext'


_MARKER = object()


class I18nTextIndexMixin(BaseIndexMixin):
    """I18n text index mixin"""

    def __init__(self, language, interface=None):
        self.interface = interface
        self.language = language

    def discriminate(self, obj, default):
        if self.interface is not None:
            obj = self.interface(obj, None)
            if obj is None:
                return default

        # pylint: disable=assignment-from-no-return
        value = II18n(obj).get_attribute(self.discriminator, lang=self.language, default=_MARKER)
        if value is _MARKER:
            return default

        if isinstance(value, Persistent):
            raise ValueError('Catalog cannot index persistent object {0!r}'.format(value))

        if isinstance(value, Broken):
            raise ValueError('Catalog cannot index broken object {0!r}'.format(value))

        return value


class I18nTextIndexWithInterface(I18nTextIndexMixin, TextIndex):
    """I18n text index"""

    # pylint: disable=too-many-arguments
    def __init__(self, language, discriminator, interface=None, lexicon=None, index=None,
                 family=None):
        I18nTextIndexMixin.__init__(self, language, interface)
        if lexicon is None:
            lexicon = Lexicon(NltkFullTextProcessor(language))
        TextIndex.__init__(self, discriminator, lexicon, index, family)
