# -*- coding: utf-8 -*-
#
# MetaTerm - A terminology management application written in Python
# Copyright (C) 2014 Diego Beraldin
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

import os

from PyQt4 import QtCore, QtGui

from src.view.enum import DefaultLanguages
from src import model as mdl


class ExportWizard(QtGui.QWizard):
    TYPE_PAGE, LANGUAGE_PAGE, THIRD_FIELD_PAGE, FINAL_PAGE = range(4)
    """Constants used as page IDs in order to create this non-linear wizard.
    """

    TYPE_CSV, TYPE_TSV = range(2)

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
        self.setPage(self.THIRD_FIELD_PAGE, ThirdFieldSelectionPage(self))
        self.setPage(self.FINAL_PAGE, FinalPage(self))
        self.resize(self._WIDTH, self._HEIGHT)
        self.show()

    @property
    def export_type(self):
        if self.field('csv_type'):
            return ExportWizard.TYPE_CSV
        else:
            return ExportWizard.TYPE_TSV

    @property
    def selected_locales(self):
        return self.page(ExportWizard.LANGUAGE_PAGE).get_selected_locales()

    @property
    def third_field(self):
        return self.page(ExportWizard.THIRD_FIELD_PAGE).third_field_property

    @property
    def output_file_path(self):
        return self.page(ExportWizard.FINAL_PAGE).get_output_file_path()


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
        self._languages = DefaultLanguages(self)
        # page title
        self.setTitle(self.tr('Select language pair'))
        # language selection widgets
        self._available_languages_view = QtGui.QListWidget(self)
        self._chosen_languages = QtGui.QListWidget(self)
        self._populate_language_views()
        # button widget
        button_widget = QtGui.QWidget(self)
        button_widget.setLayout(QtGui.QVBoxLayout(button_widget))
        select_button = QtGui.QToolButton(button_widget)
        select_button.setIcon(QtGui.QIcon(':/arrow-right'))
        select_button.clicked.connect(self._handle_language_selected)
        deselect_button = QtGui.QToolButton(button_widget)
        deselect_button.clicked.connect(self._handle_language_unselected)
        deselect_button.setIcon(QtGui.QIcon(':/arrow-left'))
        button_widget.layout().addWidget(select_button)
        button_widget.layout().addWidget(deselect_button)
        # puts it all together
        self.setLayout(QtGui.QHBoxLayout(self))
        self.layout().addWidget(self._available_languages_view)
        self.layout().addWidget(button_widget)
        self.layout().addWidget(self._chosen_languages)

    def initializePage(self):
        # shows the correct subtitle
        if self.field('csv_type'):
            subtitle = self.tr('Please select the two languages you wish to '
                               'export to the CSV file.')
        else:
            subtitle = self.tr('Please select the two languages you wish to '
                               'export to the TSV file.')
        subtitle += self.tr('The order is significant in that the first '
                            'language will be interpreted as the <strong>'
                            'source</strong> language and the second will be '
                            'interpreted as the <strong>target</strong> one.')
        self.setSubTitle(subtitle)

    def _populate_language_views(self):
        termbase_locales = mdl.get_main_model().open_termbase.languages
        for locale in termbase_locales:
            flag = QtGui.QIcon(':/flags/{0}'.format(locale))
            name = self._languages[locale]
            item = QtGui.QListWidgetItem(flag, name,
                                         self._available_languages_view)
            self._available_languages_view.addItem(item)

    @QtCore.pyqtSlot()
    def _handle_language_selected(self):
        row = self._available_languages_view.currentRow()
        item = self._available_languages_view.takeItem(row)
        # order is significant
        self._chosen_languages.addItem(item)
        self.completeChanged.emit()

    @QtCore.pyqtSlot()
    def _handle_language_unselected(self):
        row = self._chosen_languages.currentRow()
        item = self._chosen_languages.takeItem(row)
        self._available_languages_view.addItem(item)
        self._available_languages_view.sortItems(QtCore.Qt.AscendingOrder)
        self.completeChanged.emit()

    def isComplete(self):
        return (super(LanguagePage, self).isComplete()
                and self._chosen_languages.count() == 2)

    def get_selected_locales(self):
        names = [self._chosen_languages.item(index).data(QtCore.Qt.DisplayRole)
                 for index in range(self._chosen_languages.count())]
        inverted_languages = {value: key for key, value in self._languages}
        return [inverted_languages[name] for name in names]

    def nextId(self):
        if self.field('csv_type') or self.field('tsv_type'):
            return ExportWizard.THIRD_FIELD_PAGE


class ThirdFieldSelectionPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(ThirdFieldSelectionPage, self).__init__(parent)
        self._schema = mdl.get_main_model().open_termbase.schema
        self.third_field_property = None
        self.setTitle(self.tr('Select which fields to export'))
        schema = mdl.get_main_model().open_termbase.schema
        # field selection widget
        self._fields = QtGui.QListWidget(self)
        for prop in schema.get_properties('E'):
            item = QtGui.QListWidgetItem(prop.name, self._fields)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
        self._fields.itemClicked.connect(self._handle_item_clicked)
        # puts it all together
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self._fields)

    def initializePage(self):
        # shows the correct subtitle
        subtitle = self.tr('Please select exactly one field '
                           'from the list below.')
        if self.field('csv_type'):
            subtitle += (self.tr('This will be exported as the third column '
                                 ' in the resulting CSV file.'))
        else:
            subtitle += (self.tr('This will be exported as the third column '
                                 'in the resulting TSV file.'))
        self.setSubTitle(subtitle)

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def _handle_item_clicked(self, item):
        for index in range(self._fields.count()):
            current = self._fields.item(index)
            if current is not item:
                current.setCheckState(QtCore.Qt.Unchecked)
        if item.checkState() == QtCore.Qt.Checked:
            property_name = item.data(QtCore.Qt.DisplayRole)
            property_list = [p for p in self._schema.get_properties('E')
                             if p.name == property_name]
            if property_list:
                self.third_field_property = property_list.pop()
            else:
                self.third_field_property = None
        else:
            self.third_field_property = None
        self.completeChanged.emit()

    def isComplete(self):
        return self.third_field_property is not None

    def nextId(self):
        return ExportWizard.FINAL_PAGE


class FinalPage(QtGui.QWizardPage):
    def __init__(self, parent):
        super(FinalPage, self).__init__(parent)
        self.setTitle(self.tr('Select the output file'))
        self.setSubTitle(self.tr('Please select the destination '
                                 'where the resulting file should be written'))
        self._path_input = QtGui.QLineEdit(self)
        self._path_input.setEnabled(False)
        browse_button = QtGui.QPushButton(self.tr('Browse'))
        browse_button.clicked.connect(self._handle_browse_button_pressed)
        select_file_widget = QtGui.QWidget(self)
        select_file_widget.setLayout(QtGui.QHBoxLayout(select_file_widget))
        select_file_widget.layout().addWidget(self._path_input)
        select_file_widget.layout().addWidget(browse_button)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(select_file_widget)

    def _handle_browse_button_pressed(self):
        if self.field('csv_type'):
            file_filter = self.tr('Comma-separated values (*.csv)')
        elif self.field('tsv_type'):
            file_filter = self.tr('Tab-separated values (*.tsv)')
        else:
            # TODO: this must be handled
            file_filter = ''
        dialog = QtGui.QFileDialog(self, self.tr('Select output file'),
                                   os.path.expanduser('~'), file_filter)
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        if dialog.exec_():
            paths = dialog.selectedFiles()
            if paths:
                path = paths.pop().strip()
                if self.field('csv_type') and not path.endswith('.csv'):
                    path += '.csv'
                elif self.field('tsv_type') and not path.endswith('.tsv'):
                    path += '.tsv'
                self._path_input.setText(path)
        else:
            self._path_input.clear()
        self.completeChanged.emit()

    def get_output_file_path(self):
        return self._path_input.text()

    def isComplete(self):
        return len(self.get_output_file_path()) > 0
