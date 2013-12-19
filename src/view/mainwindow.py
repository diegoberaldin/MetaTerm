# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.mainwindow

This module contains the definition of the application main window and  of the
central widget that is going to be displayed inside it.
"""

from PyQt4 import QtGui, QtCore
from src import model as mdl


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
        # reference to the model
        self.model = None
        # action initialization (they are member data after all, aren't they?)
        self._new_tb_action = QtGui.QAction('New...', self)
        self._new_tb_action.triggered.connect(self._handle_new_termbase)
        self._open_tb_action = QtGui.QAction('Open...', self)
        self._open_tb_action.triggered.connect(self._handle_open_termbase)
        self._close_tb_action = QtGui.QAction('Close...', self)
        self._close_tb_action.triggered.connect(
            lambda: self.fire_event.emit('close_termbase', {}))
        self._delete_tb_action = QtGui.QAction('Delete...', self)
        self._delete_tb_action.triggered.connect(self._handle_delete_termbase)
        self._show_tb_properties_action = QtGui.QAction('Properties...', self)
        self._show_tb_properties_action.triggered.connect(
            self._handle_show_termbase_properties)
        self._show_tb_properties_action.setEnabled(False)
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
        # edit menu
        edit_menu = QtGui.QMenu('Edit', self)
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
            self._show_tb_properties_action.setEnabled(True)

    def update_for_termbase_closing(self):
        """Resets the main UI when the current termbase is closed.

        :rtype: None
        """
        self._show_tb_properties_action.setEnabled(False)
        # TODO: unfinished

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
        dialog = TermbasePropertyDialog(self.model, self)
        dialog.exec()


class MainWidget(QtGui.QWidget):
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
        self.fire_event.connect(self.parent().fire_event)
        self.setLayout(QtGui.QVBoxLayout(self))


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
        self.selected_termbase_name = None
        self.setLayout(QtGui.QVBoxLayout(self))
        # dialog content
        upper_label = QtGui.QLabel(
            'Please select a termbase from the list below:', self)
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

    def __init__(self, termbase, parent):
        """Constructor method.

        :param termbase: reference to the termbase to query for information
        :type termbase: mdl.Termbase
        :param parent: reference to the parent widget
        :type parent: QtGui.QWidget
        :rtype: TermbasePropertyDialog
        """
        super(TermbasePropertyDialog, self).__init__(parent)
        self.setWindowTitle('Termbase properties')
        self._model = termbase
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
        for locale in self._model.get_languages():
            item = QtGui.QListWidgetItem()
            item.setText(mdl.DEFAULT_LANGUAGES[locale])
            item.setIcon(QtGui.QIcon(':/flags/{0}.png'.format(locale)))
            language_view.insertItem(language_view.count(), item)
        language_group = QtGui.QGroupBox('Languages', self)
        language_group.setLayout(QtGui.QVBoxLayout(language_group))
        language_group.layout().addWidget(language_view)
        self.layout().addWidget(language_group)

    def _populate_stats_group(self):
        """Creates and fills the statistics part of the dialog, displaying
        the number of entries of the termbase and its total size on disk

        :rtype: None
        """
        stats_group = QtGui.QGroupBox('Statistics', self)
        stats_group.setLayout(QtGui.QGridLayout(stats_group))
        stats_group.layout().addWidget(
            QtGui.QLabel('Number of entries:', stats_group), 0, 0)
        stats_group.layout().addWidget(
            QtGui.QLabel(str(self._model.get_entry_number()), stats_group), 0,
            1)
        stats_group.layout().addWidget(QtGui.QLabel('Total size:', stats_group),
                                       1, 0)
        stats_group.layout().addWidget(
            QtGui.QLabel(self._model.get_size(), stats_group), 1, 1)
        self.layout().addWidget(stats_group)

    def _create_buttons(self):
        """Creates the button box of the dialog.

        :rtype: None
        """
        button_box = QtGui.QDialogButtonBox(self)
        ok_button = button_box.addButton(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)
        self.layout().addWidget(button_box)
