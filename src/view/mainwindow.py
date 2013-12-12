"""
.. currentmodule:: src.view.mainwindow

This module contains the definition of the application main window and  of the central widget that is going to be
displayed inside it.
"""

from PyQt4 import QtGui, QtCore


class MainWindow(QtGui.QMainWindow):
    """This class corresponds to the application main window.
    """
    # class-specific signals
    fire_event = QtCore.pyqtSignal(str, dict)
    'Signal is emitted whenever an event is fired in the application main window.'

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
        self.setCentralWidget(MainWidget(self))
        #self.setMinimumSize(self._MIN_WIDTH, self._MIN_HEIGHT)


class MainWidget(QtGui.QWidget):
    """Central widget that is displayed inside the application main window.
    """
    fire_event = QtCore.pyqtSignal(str, dict)
    'This signal is emitted whenever an event needs to be notified to the controller.'

    def __init__(self, parent):
        """Constructor method
    
            :param parent: reference to the main window
            :type parent: QWidget
            :rtype: MainWidget
            """
        super(MainWidget, self).__init__(parent)
        self.fire_event.connect(self.parent().fire_event)
        self.setLayout(QtGui.QVBoxLayout(self))