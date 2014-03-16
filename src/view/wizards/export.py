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
.. currentmodule:: src.view.wizards.export

This module contains the classes used to define the wizard that will guide the
user in exporting the information of the currently opened termbase.
"""

from PyQt4 import QtGui


class ExportWizard(QtGui.QWizard):
    TYPE_PAGE, LANGUAGE_PAGE, FIELD_PAGE, FINAL_PAGE = range(4)
    """Constants used as page IDs in order to create this non-linear wizard.
    """

    _WIDTH = 600
    """Default window width.
    """

    _HEIGHT = 400
    """Default window height.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent of the current widget
        :type parent: QtGui.QWidget
        :rtype: ExportWizard
        """
        super(ExportWizard, self).__init__(parent)
        self.setWindowTitle(self.tr('Export termbase data'))
        # adds the wizard pages
        self.setPage(self.TYPE_PAGE, ExportTypePage(self))
        self.setPage(self.LANGUAGE_PAGE, LanguagePage(self))
        self.setPage(self.FIELD_PAGE, FieldSelectionPage(self))
        self.setPage(self.FINAL_PAGE, FinalPage(self))
        self.resize(self._WIDTH, self._HEIGHT)
        self.show()


class ExportTypePage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(ExportTypePage, self).__init__(parent)
        self.setTitle(self.tr('Select export type'))
        self.setSubTitle(
            self.tr('Please select an output format for termbase data.'))
        type_group = QtGui.QGroupBox(self.tr('Available types'), self)
        type_group.setLayout(QtGui.QVBoxLayout(type_group))
        csv_option = QtGui.QRadioButton(
            self.tr('comma-separated values (*.csv)'), self)
        csv_option.setChecked(True)
        tsv_option = QtGui.QRadioButton(
            self.tr('tab-separated values (*.tab)'), self)
        type_group.layout().addWidget(csv_option)
        type_group.layout().addWidget(tsv_option)
        # puts it all together
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(type_group)
        # field registration
        self.registerField('csv_type', csv_option)
        self.registerField('tsv_type', tsv_option)

    def nextId(self):
        if self.field('csv_type') or self.field('tsv_type'):
            return ExportWizard.LANGUAGE_PAGE


class LanguagePage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(LanguagePage, self).__init__(parent)
        # title and subtitle
        self.setTitle(self.tr('Select language pair'))
        if self.field('csv_type'):
            subtitle = self.tr('Please select the two languages you wish to '
                               'export to the CSV file.')
        else:
            subtitle = self.tr('Please select the two languages you wish to '
                               'export to the TSV file.')
        self.setTitle(subtitle)


class FieldSelectionPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(FieldSelectionPage, self).__init__(parent)


class FinalPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(FinalPage, self).__init__(parent)
