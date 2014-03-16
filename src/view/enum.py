# -*- coding: utf-8 -*-
#
# MetaTerm - A terminology management application written in Python
# Copyright (C) 2013 Diego Beraldin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further information, contact the authors at <diego.beraldin@gmail.com>.

"""
.. currentmodule:: src.view.enum

This module contains the definition of the enumerations that are found
in the UI. Altough being fixed values, these values must be accessed
via QObject instances if a localized version of its value is needed,
in order to ensure that the tr() method be called properly so that
localization is handled at runtime.
"""

from PyQt4 import QtCore


class DefaultLanguages(QtCore.QObject):
    """Class used to mimick a dictionary of available languages, having locale
    codes as keys and localized versions of the language name as values.
    Intances of this class can be transversed in for loops as though they were
    dictionaries and accessed by key subscripting as usual.
    """
    _DEFAULT_LANGUAGES = ['en_US', 'en_GB', 'es_ES', 'fr_FR', 'it_IT',
                          'ro_RO', 'gr_GR']
    """List of the currently supported languages
    """

    def __init__(self, parent):
        """Default QObject constructor.

        :param parent: reference to the parent of the current QObject
        :rtype: DefaultLanguages
        """
        super(DefaultLanguages, self).__init__(parent)

    def __getitem__(self, item):
        """Allows instances of the class to be accessed as dictionaries
        by using keys in the subscripting operator.

        :param item: locale of the language
        :type item: str
        :return: localized version of the language with the given locale
        :rtype: str
        """
        if item not in self._DEFAULT_LANGUAGES:
            # prevents an error but possibly creates new ones
            return None
        if item == 'en_US':
            return self.tr('English (Unites States)')
        if item == 'en_GB':
            return self.tr('English (United Kingdom)')
        if item == 'es_ES':
            return self.tr('Spanish (Spain)')
        if item == 'fr_FR':
            return self.tr('French (France)')
        if item == 'it_IT':
            return self.tr('Italian (Italy)')
        if item == 'ro_RO':
            return self.tr("Romanian")
        if item == 'gr_GR':
            return self.tr('Greek')

    def __iter__(self):
        """Allows iteration if for loops returning for each invocation a
        (key, value) tuple.

        :return: a (key, value) tuple containing the locale code of the
        language and a localized version of its name
        :rtype: tuple
        """
        items = [(locale, self[locale]) for locale in self._DEFAULT_LANGUAGES]
        # sort according to localized name
        items.sort(key=lambda t: t[1])
        for item in items:
            yield item