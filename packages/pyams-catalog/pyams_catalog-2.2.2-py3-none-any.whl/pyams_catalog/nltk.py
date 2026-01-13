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

"""PyAMS_catalog.nltk module

"""

import nltk
from hypatia.text import Lexicon
from hypatia.text.interfaces import ISplitter
from zope.interface import implementer

from pyams_i18n.language import BASE_LANGUAGES
from pyams_utils.unicode import translate_string


__docformat__ = 'restructuredtext'


@implementer(ISplitter)
class NltkStemmedTextProcessor:
    """NLTK based text processor using stemmer"""

    def __init__(self, language='english'):
        if language in BASE_LANGUAGES:
            language = BASE_LANGUAGES[language].lower()
        self.language = language
        self.stemmer = nltk.stem.SnowballStemmer(language, ignore_stopwords=True)

    def process(self, lst):
        """Main process method"""
        result = []
        for s in lst:  # pylint: disable=invalid-name
            translated = translate_string(s, keep_chars="'-").replace("'", ' ')
            tokens = nltk.word_tokenize(translated, self.language)
            result += [stem for stem in [self.stemmer.stem(token) for token in tokens
                                         if token not in self.stemmer.stopwords]
                       if stem and (len(stem) > 1) and (stem not in self.stemmer.stopwords)]
        return result

    def processGlob(self, lst):  # pylint: disable=invalid-name
        """Globs processing method"""
        result = []
        for s in lst:  # pylint: disable=invalid-name
            translated = translate_string(s, keep_chars="'-*?").replace("'", ' ')
            tokens = nltk.word_tokenize(translated, self.language)
            result += [stem for stem in [self.stemmer.stem(token) for token in tokens
                                         if token not in self.stemmer.stopwords]
                       if stem and (len(stem) > 1) and (stem not in self.stemmer.stopwords)]
        return result


@implementer(ISplitter)
class NltkFullTextProcessor:
    """NLTK based full text processor"""

    def __init__(self, language='english'):
        if language in BASE_LANGUAGES:
            language = BASE_LANGUAGES[language].lower()
        self.language = language

    def process(self, lst):
        """Main processing method"""
        result = []
        for s in lst:  # pylint: disable=invalid-name
            translated = translate_string(s, keep_chars="'-").replace("'", ' ')
            result += [
                '{}*'.format(token)
                for token in nltk.word_tokenize(translated, self.language)
                if token and len(token) > 1
            ]
        return result

    def processGlob(self, lst):  # pylint: disable=invalid-name
        """Globs processing method"""
        result = []
        for s in lst:  # pylint: disable=invalid-name
            translated = translate_string(s, keep_chars="'-*?").replace("'", ' ')
            result += [
                '{}*'.format(token)
                for token in nltk.word_tokenize(translated, self.language)
                if token and len(token) > 1
            ]
        return result


def get_fulltext_lexicon(language):
    """Fulltext lexicon creator

    :param language: lexicon language code, defined with two lowercase letters ('en', 'fr'...)
    """
    return Lexicon(NltkFullTextProcessor(language=language))
