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
.. currentmodule:: src.view.main

This module contains the definition of the application main window with its
toolbar and status bar, plus the main actions and the slot which are activated
when the latter are triggered.
"""

from PyQt4 import QtGui, QtCore
from src.view.dialogs import SelectTermbaseDialog, TermbasePropertyDialog
from src.view.entry import EntryWidget
from src import model as mdl


class MainWindow(QtGui.QMainWindow):
    """This class corresponds to the application main window.
    """
    # class-specific signals
    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted when an event is fired in the application main window."""

    # a couple of class constants
    _WIDTH = 800
    """Width of the application main window at startup."""

    _HEIGHT = 600
    """Height of the application main window at startup."""

    def __init__(self):
        """Constructor method for the main window.

        :rtype: MainWindow
        """
        super(MainWindow, self).__init__()
        # initializes actions
        self.new_tb_action = None
        self.open_tb_action = None
        self.close_tb_action = None
        self.delete_tb_action = None
        self.show_tb_properties_action = None
        self.create_entry_action = None
        self.save_entry_action = None
        self.edit_entry_action = None
        self.cancel_edit_action = None
        self.delete_entry_action = None
        self.quit_action = None
        self.about_qt_action = None
        self._initialize_actions()
        # creates menus
        self._create_menus()
        # creates the main toolbar
        self._create_main_toolbar()
        # sets the central widget
        main_widget = EntryWidget(self)
        self.setCentralWidget(main_widget)
        # window size and title
        self.resize(self._WIDTH, self._HEIGHT)
        self.setWindowTitle('MetaTerm')
        # displays a message in the status bar
        self.statusBar().showMessage('Started.')
        # signal-slot connections
        main_widget.fire_event.connect(self.fire_event)
        mdl.get_main_model().termbase_opened.connect(
            self._handle_termbase_opened)
        mdl.get_main_model().termbase_closed.connect(
            self._handle_termbase_closed)

    def _initialize_actions(self):
        """Initializes the name, icons and actions that will be associated to
        the actions of the main application window.

        :rtype: None
        """
        self.new_tb_action = QtGui.QAction(QtGui.QIcon(':/document-new.png'),
                                           'New termbase...', self)
        self.new_tb_action.triggered.connect(
            lambda: self.fire_event.emit('new_termbase', {}))
        self.open_tb_action = QtGui.QAction(QtGui.QIcon(':/document-open.png'),
                                            'Open termbase...', self)
        self.open_tb_action.triggered.connect(self._handle_open_termbase)
        self.close_tb_action = QtGui.QAction(
            QtGui.QIcon(':/document-close.png'), 'Close termbase...', self)
        self.close_tb_action.triggered.connect(
            lambda: self.fire_event.emit('close_termbase', {}))
        self.close_tb_action.setEnabled(False)
        self.delete_tb_action = QtGui.QAction(QtGui.QIcon(':/user-trash.png'),
                                              'Delete termbase...', self)
        self.delete_tb_action.triggered.connect(self._handle_delete_termbase)
        self.show_tb_properties_action = QtGui.QAction(
            QtGui.QIcon(':/server-database'), 'Termbase properties...', self)
        self.show_tb_properties_action.triggered.connect(
            self._handle_show_termbase_properties)
        self.show_tb_properties_action.setEnabled(False)
        self.create_entry_action = QtGui.QAction(
            QtGui.QIcon(':/contact-new.png'), 'Insert entry', self)
        self.create_entry_action.setEnabled(False)
        self.create_entry_action.triggered.connect(
            lambda: self.fire_event.emit('new_entry', {}))
        self.save_entry_action = QtGui.QAction(
            QtGui.QIcon(':/document-save.png'), 'Save entry', self)
        self.save_entry_action.setEnabled(False)
        self.save_entry_action.triggered.connect(
            lambda: self.fire_event.emit('save_entry', {}))
        self.edit_entry_action = QtGui.QAction(
            QtGui.QIcon(':/document-edit.png'), 'Edit entry', self)
        self.edit_entry_action.setEnabled(False)
        self.edit_entry_action.triggered.connect(
            lambda: self.fire_event.emit('edit_entry', {}))
        self.cancel_edit_action = QtGui.QAction(
            QtGui.QIcon(':/dialog-cancel.png'), 'Cancel edit', self)
        self.cancel_edit_action.setEnabled(False)
        self.cancel_edit_action.triggered.connect(
            lambda: self.fire_event.emit('edit_canceled', {}))
        self.delete_entry_action = QtGui.QAction(
            QtGui.QIcon(':/user-trash.png'), 'Delete entry', self)
        self.delete_entry_action.setEnabled(False)
        self.delete_entry_action.triggered.connect(
            lambda: self.fire_event.emit('delete_entry', {}))
        self.quit_action = QtGui.QAction(QtGui.QIcon(':/application-exit.png'),
                                         'Quit', self)
        self.quit_action.triggered.connect(lambda: QtGui.qApp.quit())
        self.about_qt_action = QtGui.QAction(QtGui.QIcon(':/help-about.png'),
                                             'About Qt', self)
        self.about_qt_action.triggered.connect(
            lambda: QtGui.QMessageBox.aboutQt(self, 'About Qt'))

    def _create_menus(self):
        """Creates the menus displayed in the main application menu bar.

        :rtype: None
        """
        # termbase menu
        termbase_menu = QtGui.QMenu('Termbase', self)
        termbase_menu.addAction(self.new_tb_action)
        termbase_menu.addAction(self.open_tb_action)
        termbase_menu.addAction(self.close_tb_action)
        termbase_menu.addAction(self.delete_tb_action)
        termbase_menu.addAction(self.show_tb_properties_action)
        termbase_menu.addAction(self.quit_action)
        self.menuBar().addMenu(termbase_menu)
        # entry menu
        entry_menu = QtGui.QMenu('Entry', self)
        entry_menu.addAction(self.create_entry_action)
        entry_menu.addAction(self.save_entry_action)
        entry_menu.addAction(self.edit_entry_action)
        entry_menu.addAction(self.cancel_edit_action)
        entry_menu.addAction(self.delete_entry_action)
        self.menuBar().addMenu(entry_menu)
        # view menu
        view_menu = QtGui.QMenu('View', self)
        self.menuBar().addMenu(view_menu)
        # help menu
        help_menu = QtGui.QMenu('?', self)
        help_menu.addAction(self.about_qt_action)
        self.menuBar().addMenu(help_menu)

    def _create_main_toolbar(self):
        """Creates the application main menu bar which is displayed in the
        top area of the main window.

        :rtype: None
        """
        # termbase-related operations
        main_toolbar = QtGui.QToolBar(self)
        main_toolbar.addAction(self.open_tb_action)
        main_toolbar.addAction(self.new_tb_action)
        main_toolbar.addSeparator()
        # entry-related operations
        main_toolbar.addAction(self.create_entry_action)
        main_toolbar.addAction(self.save_entry_action)
        main_toolbar.addAction(self.edit_entry_action)
        main_toolbar.addAction(self.cancel_edit_action)
        main_toolbar.addAction(self.delete_entry_action)
        main_toolbar.addSeparator()
        # other operations
        main_toolbar.addAction(self.quit_action)
        self.addToolBar(main_toolbar)

    def display_message(self, message):
        """Displays a message in the application status bar.

        :param message: the message to be displayed
        :type message: str
        :rtype: None
        """
        self.statusBar().showMessage(message)

    @QtCore.pyqtSlot()
    def _handle_open_termbase(self):
        """Asks the user to select a termbase from the available ones and, if
        some is actually selected, informs the controller about the event
        (passing in the termbase name).

        :rtype: None
        """
        dialog = SelectTermbaseDialog(self)
        ret = dialog.exec()
        if ret:  # informs the controller
            self.fire_event.emit('open_termbase', {
                'name': dialog.selected_termbase_name})

    @QtCore.pyqtSlot()
    def _handle_termbase_opened(self):
        """This slot is activated when the view detects that in the model a
        new termbase has been opened. In this case the correct reaction is to
        enable the property action.

        :rtype: None
        """
        self.show_tb_properties_action.setEnabled(True)
        self.close_tb_action.setEnabled(True)
        self.create_entry_action.setEnabled(True)

    @QtCore.pyqtSlot()
    def _handle_termbase_closed(self):
        """Resets the main UI when the current termbase is closed, this slot is
        activated when the GUI detects that the model has changed.

        :rtype: None
        """
        self.show_tb_properties_action.setEnabled(False)
        self.close_tb_action.setEnabled(False)
        self.create_entry_action.setEnabled(False)

    @QtCore.pyqtSlot()
    def _handle_delete_termbase(self):
        """This slot is activated when the user requires to delete a termbase,
        it has the responsibility of displaying a dialog to allow users to
        select which termbase they want to be deleted and, if a valid entry is
        selected, it displays a last warning. Only if the user confirms the
        operation is the termbase eventually deleted (by the controller).

        :rtype: None
        """
        dialog = SelectTermbaseDialog(self)
        ret = dialog.exec()
        if ret:
            warning = QtGui.QMessageBox(self)
            warning.setWindowTitle(Warning)
            warning.setText('Are you sure you want to delete this termbase?')
            warning.setInformativeText('The operation cannot be undone, do you '
                                       'still want to proceed?')
            warning.setStandardButtons(
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            ret = warning.exec()
            if ret:
                self.fire_event.emit('delete_termbase', {
                    'name': dialog.selected_termbase_name})

    @QtCore.pyqtSlot()
    def _handle_show_termbase_properties(self):
        """Displays a dialog window with some termbase properties.

        :rtype: None
        """
        dialog = TermbasePropertyDialog(self)
        dialog.exec()
