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
    """Wizard that has the responsibility of guiding end users through the
    procedure of exporting the currently opened termbase to a file.
    """
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
        """Returns a constant value corresponding to the export type selected
        by the user in the ExportTypePage. Returned values correspond to
        the ExportWizard.TYPE_TSV and ExportWizard.TYPE_CSV constants.

        :return: a constant defining the selected export type
        :rtype: int
        """
        if self.field('csv_type'):
            return ExportWizard.TYPE_CSV
        else:
            return ExportWizard.TYPE_TSV

    @property
    def selected_locales(self):
        """List of locales corresponding to the selected languages. The
        returned list is ordered and the first item must be interpreted
        as the source language of the exported termbase.

        :return: the list of the selected locales
        :rtype: list
        """
        return self.page(ExportWizard.LANGUAGE_PAGE).selected_locales

    @property
    def third_field(self):
        """Property object that has been selected as the third field for
        a CSV or TSV termbase export.

        :return: the property object
        :rtype: src.model.dataaccess.schema.Property
        """
        return self.page(ExportWizard.THIRD_FIELD_PAGE).third_field_property

    @property
    def third_field_details(self):
        return self.page(ExportWizard.THIRD_FIELD_PAGE).third_field_property_details

    @property
    def output_file_path(self):
        """Path of the file that has been selected to contain the exported
        termbase.

        :return: path of the output file
        :rtype: str
        """
        return self.page(ExportWizard.FINAL_PAGE).output_file_path


class ExportTypePage(QtGui.QWizardPage):
    """Page of the wizard where users can choose in which for to export
    their data, e.g. comma-separated or tab-separated values.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtGui.QWidget
        :rtype: ExportTypePage
        """
        super(ExportTypePage, self).__init__(parent)
        # sets title and subtitle
        self.setTitle(self.tr('Select export type'))
        self.setSubTitle(
            self.tr('Please select an output format for termbase data.'))
        # list of export format options
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
        """Overridden in order to return the correct page id according
        to the user's choice.

        :return: id of the next page
        :rtype: int
        """
        if self.field('csv_type') or self.field('tsv_type'):
            return ExportWizard.LANGUAGE_PAGE


class LanguagePage(QtGui.QWizardPage):
    """Page of the wizard where users can select the languages they wish to
    export. The first language is currently interpreted as the source language,
    in case of 'directed' export formats such as CSV or TSV.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtGui.QWidget
        :rtype: LanguagePage
        """
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
        """Overridden in order to correctly set the subtitle, which depends on
        previous choices and cannot be added upon instantiation
        :rtype: None
        """
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
        """Utility method used to populate the available language list.
        :rtype: None
        """
        termbase_locales = mdl.get_main_model().open_termbase.languages
        for locale in termbase_locales:
            flag = QtGui.QIcon(':/flags/{0}'.format(locale))
            name = self._languages[locale]
            item = QtGui.QListWidgetItem(flag, name,
                                         self._available_languages_view)
            self._available_languages_view.addItem(item)

    @QtCore.pyqtSlot()
    def _handle_language_selected(self):
        """Moves the QtGui.QListWidgetItem corresponding to the
        selected language from the list of available languages to
        the list of the selected ones.

        :rtype: None
        """
        row = self._available_languages_view.currentRow()
        item = self._available_languages_view.takeItem(row)
        # order is significant
        self._chosen_languages.addItem(item)
        self.completeChanged.emit()

    @QtCore.pyqtSlot()
    def _handle_language_unselected(self):
        """Moves the QtGui.QListWidgetItem corresponding to the
        selected language back from the list of selected languages to
        the list of the available ones.

        :rtype: None
        """
        row = self._chosen_languages.currentRow()
        item = self._chosen_languages.takeItem(row)
        self._available_languages_view.addItem(item)
        self._available_languages_view.sortItems(QtCore.Qt.AscendingOrder)
        self.completeChanged.emit()

    def isComplete(self):
        """Overridden in order to return True only if two languages have
        been chosen by the user.

        :return: True if exactly 2 languages have been chosen by the user,
        False otherwise
        :rtype: bool
        """
        return (super(LanguagePage, self).isComplete()
                and self._chosen_languages.count() == 2)

    @property
    def selected_locales(self):
        """List of the locales corresponding to the languages that the user has
        selected in the wizard page.

        :return: ordered list of the selected locales, where the first one is
        to be interpreted as the source language
        :rtype: list
        """
        names = [self._chosen_languages.item(index).data(QtCore.Qt.DisplayRole)
                 for index in range(self._chosen_languages.count())]
        inverted_languages = {value: key for key, value in self._languages}
        return [inverted_languages[name] for name in names]

    def nextId(self):
        """Overridden in order to return the id of the next page.

        :return: id of the next page in the wizard
        :rtype: int
        """
        if self.field('csv_type') or self.field('tsv_type'):
            return ExportWizard.THIRD_FIELD_PAGE


class ThirdFieldSelectionPage(QtGui.QWizardPage):
    """Wizard page where users can select the third field that will
    be exported in simple delimited formats such as CSV or TSV.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtGui.QWidget
        :rtype: ThirdFieldSelectionPage
        """
        super(ThirdFieldSelectionPage, self).__init__(parent)
        self._schema = mdl.get_main_model().open_termbase.schema
        self.third_field_property = None
        self.third_field_property_details = None
        self.setTitle(self.tr('Select which fields to export'))
        schema = mdl.get_main_model().open_termbase.schema
        # field selection widget
        self._fields = QtGui.QListWidget(self)
        # adds a list item for each entry level property
        for prop in schema.get_properties('E'):
            item = QtGui.QListWidgetItem(prop.name, self._fields)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setData(QtCore.Qt.UserRole, (prop, 'entry'))
        # adds two list items for each term level property (source and target)
        for prop in self._schema.get_properties('T'):
            source_item = QtGui.QListWidgetItem('{0} (source)'.format(prop.name), self._fields)
            source_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            source_item.setCheckState(QtCore.Qt.Unchecked)
            source_item.setData(QtCore.Qt.UserRole, (prop, 'term_source'))
            target_item = QtGui.QListWidgetItem('{0} (target)'.format(prop.name), self._fields)
            target_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            target_item.setCheckState(QtCore.Qt.Unchecked)
            target_item.setData(QtCore.Qt.UserRole, (prop, 'term_target'))
        self._fields.itemClicked.connect(self._handle_item_clicked)
        # puts it all together
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self._fields)

    def initializePage(self):
        """Shows the correct subtitle, which depends on previous user choices
        and cannot be statically determined upon class instantiation.

        :rtype: None
        """
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
        """Marks as unselected every other checked fields and stores
        internally the selected property.

        :param item: currently activated list item
        :type item: QtGui.QListWidgetItem
        :rtype: None
        """
        for index in range(self._fields.count()):
            current = self._fields.item(index)
            if current is not item:
                # other fields must be unselected
                current.setCheckState(QtCore.Qt.Unchecked)
        if item.checkState() == QtCore.Qt.Checked:
            # remembers the property that has been selected
            prop, prop_detail = item.data(QtCore.Qt.UserRole)
            self.third_field_property = prop
            if prop_detail == 'term_source':
                self.third_field_property_details = 'source'
            elif prop_detail == 'term_target':
                self.third_field_property_details = 'target'
            else:
                self.third_field_property_details = None
        else:
            self.third_field_property = None
            self.third_field_property_details = None
        self.completeChanged.emit()

    def isComplete(self):
        """Determines whether the user has completed this step based on
        whether they have chosen the property to be exported.

        :return: True if the page is complete, False otherwise
        :rtype: bool
        """
        # TODO: the third field is actually optional!
        return self.third_field_property is not None

    def nextId(self):
        """Goes straight to the final page.

        :return: id of the next wizard page
        :rtype: int
        """
        return ExportWizard.FINAL_PAGE


class FinalPage(QtGui.QWizardPage):
    """Final page of the export wizard, where users can eventually select the
    output file where the exported data will be persisted.
    """

    def __init__(self, parent):
        """Constructor method

        :param parent: reference to the widget parent
        :type parent: QtGui.QWidget
        :rtype: FinalPage
        """
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

    @QtCore.pyqtSlot()
    def _handle_browse_button_pressed(self):
        """Shows a dialog allowing users to select the output file and shows
        its path in the associated QtGui.QLineEdit in the page.

        :rtype: None
        """
        if self.field('csv_type'):
            file_filter = self.tr('Comma-separated values (*.csv)')
        elif self.field('tsv_type'):
            file_filter = self.tr('Tab-separated values (*.tsv)')
        else:
            # TODO: this must be handled
            file_filter = ''
        # shows a dialog to pick file
        dialog = QtGui.QFileDialog(self, self.tr('Select output file'),
                                   os.path.expanduser('~'), file_filter)
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        if dialog.exec_():
            paths = dialog.selectedFiles()
            if paths:
                path = paths.pop().strip()
                # appends file extension if missing
                if self.field('csv_type') and not path.endswith('.csv'):
                    path += '.csv'
                elif self.field('tsv_type') and not path.endswith('.tsv'):
                    path += '.tsv'
                # saves the output path
                self._path_input.setText(path)
        else:
            self._path_input.clear()
        self.completeChanged.emit()

    @property
    def output_file_path(self):
        """Path of the file where the termbase should be exported.
        :return: the selected path or '' if none was selected
        :rtype: str
        """
        return self._path_input.text()

    def isComplete(self):
        """Overridden in order to state whether the page is complete based on
        the user having selected an output file or not.
        :return: True if the user has selected an output path, False otherwise
        :rtype: bool
        """
        return len(self.output_file_path) > 0
