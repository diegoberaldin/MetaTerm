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
.. currentmodule:: src.view.dialogs

This module contains the definition of the dialog windows that are used to
interact with the end user by collecting input data or simply displaying some
pieces of information of interest.
"""

from PyQt4 import QtCore, QtGui

from src import model as mdl
from src.view.enum import DefaultLanguages


class SelectTermbaseDialog(QtGui.QDialog):
    """Simple dialog where one among the available termbase can be chosen. It
    must display a list of the possible termbase names depending on the content
    of the termbase directory in the local system, and allow the user to select
    one among them to open it.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: the dialog parent widget
        :type parent: QtCore.QWidget
        :rtype: SelectTermbaseDialog
        """
        super(SelectTermbaseDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('Select termbase'))
        self.selected_termbase_name = None
        self.setLayout(QtGui.QVBoxLayout(self))
        # dialog content
        upper_label = QtGui.QLabel(
            self.tr('Please select a termbase from the list below:'), self)
        upper_label.setWordWrap(True)
        self._view = QtGui.QListView(self)
        self._view.setModel(QtGui.QStringListModel(mdl.get_termbase_names()))
        # button box
        button_box = QtGui.QDialogButtonBox(self)
        ok_button = button_box.addButton(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self._handle_ok_pressed)
        cancel_button = button_box.addButton(QtGui.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # puts it all together
        self.layout().addWidget(upper_label)
        self.layout().addWidget(self._view)
        self.layout().addWidget(button_box)

    @QtCore.pyqtSlot()
    def _handle_ok_pressed(self):
        """Defines the dialog behaviour when the user presses the 'Ok' button of
        the dialog.

        :rtype: None
        """
        selected_indexes = self._view.selectedIndexes()
        if not selected_indexes:  # nothing to do, operation cancelled
            self.reject()
        else:
            # extracts the name of the selected termbase
            name = self._view.model().data(selected_indexes[0],
                                           QtCore.Qt.DisplayRole)
            self.selected_termbase_name = '.'.join(name.split('.')[:-1])
            super(SelectTermbaseDialog, self).accept()


class TermbasePropertyDialog(QtGui.QDialog):
    """Dialog window used to display read-only information about the currently
    open termbase such as the languages involved, the number of entries it
    contains and the space occupied on disk.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtGui.QWidget
        :rtype: TermbasePropertyDialog
        """
        super(TermbasePropertyDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('Termbase properties'))
        self.setLayout(QtGui.QVBoxLayout(self))
        self._populate_language_group()
        self._populate_stats_group()
        self._create_buttons()

    def _populate_language_group(self):
        """Creates and fills the party of the dialog concerning the languages
        that are involved in the termbase entries.

        :rtype: None
        """
        language_view = QtGui.QListWidget(self)
        for locale in mdl.get_main_model().open_termbase.languages:
            item = QtGui.QListWidgetItem()
            item.setText(DefaultLanguages(self)[locale])
            item.setIcon(QtGui.QIcon(':/flags/{0}.png'.format(locale)))
            language_view.insertItem(language_view.count(), item)
        language_group = QtGui.QGroupBox(self.tr('Languages'), self)
        language_group.setLayout(QtGui.QVBoxLayout(language_group))
        language_group.layout().addWidget(language_view)
        self.layout().addWidget(language_group)

    def _populate_stats_group(self):
        """Creates and fills the statistics part of the dialog, displaying
        the number of entries of the termbase and its total size on disk

        :rtype: None
        """
        stats_group = QtGui.QGroupBox(self.tr('Statistics'), self)
        stats_group.setLayout(QtGui.QGridLayout(stats_group))
        stats_group.layout().addWidget(
            QtGui.QLabel(self.tr('Number of entries:'), stats_group), 0, 0)
        tb = mdl.get_main_model().open_termbase
        stats_group.layout().addWidget(
            QtGui.QLabel(str(tb.entry_number), stats_group), 0,
            1)
        stats_group.layout().addWidget(QtGui.QLabel(self.tr('Total size:'),
                                                    stats_group), 1, 0)
        stats_group.layout().addWidget(
            QtGui.QLabel(tb.size, stats_group), 1, 1)
        self.layout().addWidget(stats_group)

    def _create_buttons(self):
        """Creates the button box of the dialog.

        :rtype: None
        """
        button_box = QtGui.QDialogButtonBox(self)
        ok_button = button_box.addButton(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)
        self.layout().addWidget(button_box)
