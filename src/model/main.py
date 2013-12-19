# -*- coding: utf-8 -*-

from PyQt4 import QtCore

_MAIN_MODEL = None


def get_main_model():
    global _MAIN_MODEL
    if not _MAIN_MODEL:
        _MAIN_MODEL = MainModel()
    return _MAIN_MODEL


class MainModel(QtCore.QObject):

    _instance = None
    """Reference to the single instance of this module.
    """

    termbase_opened = QtCore.pyqtSignal()
    """Signal emitted when a new termbase is opened.
    """

    termbase_closed = QtCore.pyqtSignal()
    """Signal emitted whenever the open termbase gets closed.
    """

    def __init__(self):
        super(MainModel, self).__init__()
        self._open_termbase = None

    @property
    def open_termbase(self):
        return self._open_termbase

    @open_termbase.setter
    def open_termbase(self, value):
        self._open_termbase = value
        if value:
            self.termbase_opened.emit()
        else:
            self.termbase_closed.emit()
