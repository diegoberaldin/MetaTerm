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
        self.setMinimumSize(self._MIN_WIDTH, self._MIN_HEIGHT)
        # action initialization (they are member data after all, aren't they?)
        self._new_tb_action = QtGui.QAction('New termbase...', self)
        self._new_tb_action.triggered.connect(self._handle_new_termbase)
        self._open_tb_action = QtGui.QAction('Open termbase...', self)
        self._open_tb_action.triggered.connect(self._handle_open_termbase)
        self._about_qt_action = QtGui.QAction('About Qt', self)
        self._about_qt_action.triggered.connect(
            lambda: QtGui.QMessageBox.aboutQt(self, 'About Qt'))
        self._create_menus()
        self.setCentralWidget(MainWidget(self))
        self.setWindowTitle('MetaTerm')

    def _create_menus(self):
        """Creates the menus displayed in the main application menu bar.

        :rtype: None
        """
        file_menu = QtGui.QMenu('File', self)
        file_menu.addAction(self._new_tb_action)
        file_menu.addAction(self._open_tb_action)
        edit_menu = QtGui.QMenu('Edit', self)
        view_menu = QtGui.QMenu('View', self)
        help_menu = QtGui.QMenu('?', self)
        help_menu.addAction(self._about_qt_action)
        self.menuBar().addMenu(file_menu)
        self.menuBar().addMenu(edit_menu)
        self.menuBar().addMenu(view_menu)
        self.menuBar().addMenu(help_menu)

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
        open_termbase_dialog = OpenTermbaseDialog(self)
        ret = open_termbase_dialog.exec()
        if ret:  # informs the controller
            self.fire_event.emit('open_termbase', {
            'name': open_termbase_dialog.selected_termbase_name})


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


class OpenTermbaseDialog(QtGui.QDialog):
    def __init__(self, parent):
        """Creates a simple dialog where one among the available termbase can be
        chosen by the user.

        :param parent: the dialog parent widget
        :type parent: QWidget
        :rtype: OpenTermbaseDialog
        """
        super(OpenTermbaseDialog, self).__init__(parent)
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
            self.selected_termbase_name = self._view.model().data(
                selected_indexes[0], QtCore.Qt.DisplayRole)
            super(OpenTermbaseDialog, self).accept()
