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
.. currentmodule:: src.model.main

This module contains the implementation of the main model, which is a Singleton
class used to store information about the shared state of the  application model
such as the currently opened (main) termbase.
"""

from PyQt4 import QtCore

_MAIN_MODEL = None
"""Reference to the single instance of the main model of the application.
"""


def get_main_model():
    """Returns a reference to the application main model, creating an instance
    of it if accessed for the first time (lazy initialization).

    :returns: reference to the application main model
    :rtype: MainModel
    """
    global _MAIN_MODEL
    if not _MAIN_MODEL:
        _MAIN_MODEL = MainModel()
    return _MAIN_MODEL


class MainModel(QtCore.QObject):
    """High level representation of the application 'main model', i.e. the
    shared state of the application model which carries information such as the
    currently opened main termbase. This model has also the responsibility of
    emitting signals when the changes occurring in it must trigger a reaction
    in the application GUI, e.g. when the main termbase is changed.
    """

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
        """Constructor method. This should *never* be called from outside this
        module, use the ``get_main_model()`` top-level function to obtain a
        reference to the application main model instead.

        :rtype: MainModel
        """
        super(MainModel, self).__init__()
        self._open_termbase = None

    @property
    def open_termbase(self):
        """Returns a ``model.dataaccess.termbase.Termbase`` reference pointing
        to the currently opened (main) termbase of the application.

        :returns: a reference to the currently opened termbase
        :rtype: Termbase
        """
        return self._open_termbase

    @open_termbase.setter
    def open_termbase(self, value):
        """Changes the currently opened (main) termbase in the application model
        informing the views of the change. If the passed-in value is None, the
        currently opened termbase gets closed.

        :param value: reference to the new termbase being opened or None
        :type value: Termbase
        :rtype: None
        """
        self._open_termbase = value
        if value:
            self.termbase_opened.emit()
        else:
            self.termbase_closed.emit()
