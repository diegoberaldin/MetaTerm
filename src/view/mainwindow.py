# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.mainwindow

This module contains the definition of the application main window and  of the
central widget that is going to be displayed inside it.
"""

from PyQt4 import QtGui, QtCore
from src.view.dialogs import SelectTermbaseDialog, TermbasePropertyDialog
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


class EntryList(QtGui.QWidget):
    """List of all the entries that are stored in the current termbase.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtCore.QWidget
        :rtype: EntryList
        """
        super(EntryList, self).__init__(parent)
        self._model = None
        self._view = QtGui.QListView(self)
        selector = LanguageSelector(self)
        # puts everything together
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(selector)
        self.layout().addWidget(self._view)
        # signal-slot connection
        selector.fire_event.connect(self.fire_event)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value
        self._view.setModel(self._model)


class LanguageSelector(QtGui.QWidget):
    """This widget corresponds to the upper part of the entry list and it
    basically displays a combobox in order for the user to change the main
    language in which the termbase is displayed.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent of the widget
        :type parent: QtCore.QWidget
        :rtype: LanguageSelector
        """
        super(LanguageSelector, self).__init__(parent)
        self.setLayout(QtGui.QHBoxLayout(self))
        self.layout().addWidget(QtGui.QLabel('Language', self))
        self._language_combo = QtGui.QComboBox(self)
        self.layout().addWidget(self._language_combo)
        # signal-slot connection
        mdl.get_main_model().termbase_opened.connect(
            self._regenerate_language_list)
        mdl.get_main_model().termbase_closed.connect(
            self._regenerate_language_list)
        self._language_combo.currentIndexChanged.connect(
            self._handle_index_changed)

    @QtCore.pyqtSlot()
    def _regenerate_language_list(self):
        """Updates the list of the current languages depending on the languages
        that are available in the currently opened termbase. If the slot is
        activated upon a termbase closure, the list of languages is emptied.

        :rtype: None
        """
        if mdl.get_main_model().open_termbase:  # termbase opened
            locale_list = [mdl.DEFAULT_LANGUAGES[locale] for locale in
                           mdl.get_main_model().open_termbase.get_languages()]
        else:  # termbase closed
            locale_list = []
        model = QtGui.QStringListModel(locale_list)
        self._language_combo.setModel(model)

    @QtCore.pyqtSlot(int)
    def _handle_index_changed(self, index):
        """Determines the locale of the currently selected index in the
        language combobox and has the language selector to emit the right
        signal (with the current locale passed as a parameter)

        :param index: index of the combobox in the language selector
        :type index: int
        :rtype: None
        """
        language_name = self._language_combo.currentText()
        if language_name:
            inverted_languages = {value: key for key, value in
                                  mdl.DEFAULT_LANGUAGES.items()}
            self.fire_event.emit('language_changed',
                                 {'locale': inverted_languages[language_name]})


class EntryDisplay(QtGui.QWidget):
    """This class is used to model the main part of the application GUI, where
    terminological entries are displayed, edited and created.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the containing (main) widget
        :type parent: QtGui.QWidget
        :rtype: EntryDisplay
        """
        super(EntryDisplay, self).__init__(parent)
