# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.main

This module contains the definition of the application main window and  of the
central widget that is going to be displayed inside it.
"""

from PyQt4 import QtGui, QtCore
from src.view.dialogs import SelectTermbaseDialog, TermbasePropertyDialog
from src import model as mdl
from src.view.entry import EntryDisplay, EntryList


class MainWindow(QtGui.QMainWindow):
    """This class corresponds to the application main window.
    """
    # class-specific signals
    fire_event = QtCore.pyqtSignal(str, dict)
    'Signal emitted whenever an event is fired in the application main window.'

    # a couple of class constants
    _MIN_WIDTH = 500
    'Minimum width of the application main window.'

    _MIN_HEIGHT = 300
    'Minimum height of the application main window.'

    def __init__(self):
        """Constructor method for the main window.

        :rtype: MainWindow
        """
        super(MainWindow, self).__init__()
        # action initialization (they are member data after all, aren't they?)
        self._new_tb_action = QtGui.QAction('New...', self)
        self._new_tb_action.triggered.connect(self._handle_new_termbase)
        self._open_tb_action = QtGui.QAction('Open...', self)
        self._open_tb_action.triggered.connect(self._handle_open_termbase)
        self._close_tb_action = QtGui.QAction('Close...', self)
        self._close_tb_action.triggered.connect(
            lambda: self.fire_event.emit('close_termbase', {}))
        self._close_tb_action.setEnabled(False)
        self._delete_tb_action = QtGui.QAction('Delete...', self)
        self._delete_tb_action.triggered.connect(self._handle_delete_termbase)
        self._show_tb_properties_action = QtGui.QAction('Properties...', self)
        self._show_tb_properties_action.triggered.connect(
            self._handle_show_termbase_properties)
        self._show_tb_properties_action.setEnabled(False)
        self._create_entry_action = QtGui.QAction('Create new', self)
        self._create_entry_action.triggered.connect(self._handle_create_entry)
        self._quit_action = QtGui.QAction('Quit', self)
        self._quit_action.triggered.connect(lambda: QtGui.qApp.quit())
        self._about_qt_action = QtGui.QAction('About Qt', self)
        self._about_qt_action.triggered.connect(
            lambda: QtGui.QMessageBox.aboutQt(self, 'About Qt'))
        self._create_menus()
        # sets the central widget
        self.setCentralWidget(MainWidget(self))
        # window size and title
        self.setMinimumSize(self._MIN_WIDTH, self._MIN_HEIGHT)
        self.setWindowTitle('MetaTerm')
        # displays a message in the status bar
        self.statusBar().showMessage('Started.')
        # signal-slot connections
        mdl.get_main_model().termbase_opened.connect(
            self._handle_termbase_opened)
        mdl.get_main_model().termbase_closed.connect(
            self._handle_termbase_closed)

    def _create_menus(self):
        """Creates the menus displayed in the main application menu bar.

        :rtype: None
        """
        # termbase menu
        termbase_menu = QtGui.QMenu('Termbase', self)
        termbase_menu.addAction(self._new_tb_action)
        termbase_menu.addAction(self._open_tb_action)
        termbase_menu.addAction(self._close_tb_action)
        termbase_menu.addAction(self._delete_tb_action)
        termbase_menu.addAction(self._show_tb_properties_action)
        termbase_menu.addAction(self._quit_action)
        self.menuBar().addMenu(termbase_menu)
        # entry menu
        edit_menu = QtGui.QMenu('Entry', self)
        self.menuBar().addMenu(edit_menu)
        # view menu
        view_menu = QtGui.QMenu('View', self)
        self.menuBar().addMenu(view_menu)
        # help menu
        help_menu = QtGui.QMenu('?', self)
        help_menu.addAction(self._about_qt_action)
        self.menuBar().addMenu(help_menu)

    def display_message(self, message):
        """Displays a message in the application status bar.

        :param message: the message to be displayed
        :type message: str
        :rtype: None
        """
        self.statusBar().showMessage(message)

    @QtCore.pyqtSlot()
    def _handle_new_termbase(self):
        """This slot does nothing except activating the new termbase wizard.

        :rtype: None
        """
        self.fire_event.emit('new_termbase', {})

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
        self._show_tb_properties_action.setEnabled(True)
        self._close_tb_action.setEnabled(True)

    @QtCore.pyqtSlot()
    def _handle_termbase_closed(self):
        """Resets the main UI when the current termbase is closed, this slot is
        activated when the GUI detects that the model has changed.

        :rtype: None
        """
        self._show_tb_properties_action.setEnabled(False)
        self._close_tb_action.setEnabled(False)

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
            button = QtGui.QMessageBox.warning(self, 'Warning',
                                               'The operation cannot '
                                               'be undone, do you '
                                               'want to proceed?')
            if button == QtGui.QMessageBox.Ok:
                self.fire_event.emit('delete_termbase', {
                    'name': dialog.selected_termbase_name})

    @QtCore.pyqtSlot()
    def _handle_show_termbase_properties(self):
        """Displays a dialog window with some termbase properties.

        :rtype: None
        """
        dialog = TermbasePropertyDialog(self)
        dialog.exec()

    @QtCore.pyqtSlot()
    def _handle_create_entry(self):
        self.centralWidget().create_entry()


class MainWidget(QtGui.QSplitter):
    """Central widget that is displayed inside the application main window.
    """
    fire_event = QtCore.pyqtSignal(str, dict)
    'Signal emitted whenever an event needs to be notified to the controller.'

    def __init__(self, parent):
        """Constructor method

            :param parent: reference to the main window
            :type parent: QWidget
            :rtype: MainWidget
            """
        super(MainWidget, self).__init__(parent)
        self._model = None
        self.fire_event.connect(self.parent().fire_event)
        self._entry_list = EntryList(self)
        self._entry_display = EntryDisplay(self)
        # puts everything together
        self.addWidget(self._entry_list)
        self.addWidget(self._entry_display)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._entry_list.model = value

    def create_entry(self):
        pass