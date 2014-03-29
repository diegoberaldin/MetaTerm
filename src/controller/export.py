# -*- coding: utf-8 -*-
#
# MetaTerm - A terminology management application written in Python
# Copyright (C) 2014 Diego Beraldin
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

import csv

from PyQt4 import QtCore

from src.controller.abstract import AbstractController
from src.view import ExportWizard
from src import model as mdl


class ExportController(AbstractController):
    def __init__(self, view):
        super(ExportController, self).__init__()
        self._view = view
        self._model = mdl.get_main_model()
        # signal-slot connection
        self._view.rejected.connect(self.finished)
        self._view.accepted.connect(self._handle_wizard_accepted)

    def _get_values(self):
        third_field = self._view.third_field
        locales = self._view.selected_locales
        result = []
        for entry in self._model.open_termbase.entries:
            source_terms = entry.get_terms(locales[0])
            target_terms = entry.get_terms(locales[1])
            third_value = entry.get_property(third_field.prop_id)
            result.extend([
                {'source': s.lemma, 'target': t.lemma, 'third': third_value}
                for s in source_terms for t in target_terms
            ])
        return result

    def _write_to_csv(self):
        output_path = self._view.output_file_path
        values = self._get_values()
        with open(output_path, 'w') as file_handle:
            writer = csv.DictWriter(file_handle,
                                    ['source', 'target', 'third'],
                                    quoting=csv.QUOTE_MINIMAL)
            writer.writerows(values)

    def _write_to_tsv(self):
        output_path = self._view.output_file_path
        values = self._get_values()
        with open(output_path, 'w') as file_handle:
            writer = csv.DictWriter(file_handle,
                                    ['source', 'target', 'third'],
                                    delimiter='\t',
                                    quoting=csv.QUOTE_MINIMAL)
            writer.writerows(values)


    @QtCore.pyqtSlot()
    def _handle_wizard_accepted(self):
        export_type = self._view.export_type
        if export_type == ExportWizard.TYPE_CSV:
            self._write_to_csv()
        elif export_type == ExportWizard.TYPE_TSV:
            self._write_to_tsv()
        self.finished.emit()
