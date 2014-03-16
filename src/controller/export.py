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
.. currentmodule:: src.controller.entry

This module contains the controller that governs entry creation, update and
deletion and manages entry visualization in the graphical user interface.
"""

from PyQt4 import QtCore

from src.controller.abstract import AbstractController
from src.model import get_main_model


class ExportController(AbstractController):
    def __init__(self, view):
        super(ExportController, self).__init__()
        self._view = view
        self._model = get_main_model().open_termbase
        # signal-slot connection
        self._view.rejected.connect(self.finished)
        self._view.finished.connect(self._handle_wizard_finished)

    @QtCore.pyqtSlot()
    def _handle_wizard_finished(self):
        # TODO: unfinished!
        self.finished.emit()
