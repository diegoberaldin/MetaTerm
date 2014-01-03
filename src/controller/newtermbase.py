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
.. currentmodule:: src.controller.newtermbase


This module contains the controller that is used in order to handle events that
are generated in the new termbase wizard, i.e. the wizard used to create a new
terminological database.
"""

from PyQt4 import QtCore
from src.controller.abstract import AbstractController
from src import model as mdl


class NewTermbaseController(AbstractController):
    """This controller is associated with the new termbase wizard and is
    responsible of keeping the termbase definition model up-to-date with the
    modification requested by the user to the termbase structure, as well as
    processing the data entered by the user when they confirm that a new
    termbase must be created.
    """

    def __init__(self, model, wizard):
        """Constructor method.

        :param model: reference to the model
        :type model: mdl.TermbaseDefinitionModel
        :param wizard: reference to the graphical user interface
        :type wizard: gui.NewTermbaseWizard
        :rtype: NewTermbaseController
        """
        super(NewTermbaseController, self).__init__()
        self._view = wizard
        self._view.fire_event.connect(self.handle_event)
        self._model = model
        # signal-slot connection
        self._view.rejected.connect(self.finished)

    @QtCore.pyqtSlot()
    def _handle_termbase_created(self):
        """This slot is activated when the user presses the 'finish' button of
        the wizard, it collects all the data that have either been stored in
        wizard fields or in the associated model and save the information on
        disk.
        """
        termbase_name = self._view.get_termbase_name()
        new_tb = mdl.Termbase(termbase_name)
        self._populate_languages(new_tb)
        self._populate_properties(new_tb)
        self.finished.emit()

    def _populate_languages(self, termbase):
        """Adds the languages that have been chosen in the UI to the newly
        created termbase.

        :param termbase: termbase to be populated
        :type termbase: mdl.Termbase
        :rtype: None
        """
        locales = self._view.get_termbase_locales()
        for locale in locales:
            termbase.add_language(locale)

    def _populate_properties(self, termbase):
        """Queries the termbase definition model for the propeties that have
        been added during configuration and adds them to the actual termbase
        structure on disk.

        :param termbase: reference to the termbase to be populated
        :type termbase: mdl.Termbase
        :rtype: None
        """
        for prop_dictionary in self._model.get_properties():
            termbase.schema.add_property(**prop_dictionary)

    def _handle_new_property(self, name, prop_type, level, values=()):
        """This event handler is activated whenever the user asks to add a new
        property to the termbase definition model.

        :param name: name of the new property
        :type name: str
        :param prop_type: type of the new property in ``['T', 'I', 'P']``
        :type prop_type: str
        :param level: level where the new property must be added
        :type level: str
        :param values: set of possible values for a picklist property
        :type values: tuple
        :rtype: None
        """
        node = mdl.PropertyNode(name=name, prop_type=prop_type, values=values)
        self._model.insert_node(level, node)

    def _handle_delete_property(self, old_node):
        """Event handler activated when the user requires to delete a property
        from the termbase definition structure.

        :param old_node: node referring to the property to delete
        :type old_node: mdl.PropertyNode
        :rtype: None
        """
        self._model.delete_node(old_node)

    def _handle_change_property(self, name, prop_type, level, old_node,
                                values=()):
        """Event handler activated when the user requires to change the
        definition of a property altering its name, type, or the set of
        possible values in case of a picklist property.

        :param name: new name of the property
        :type name: str
        :param prop_type: type of the property in ``['T', 'I', 'P']``
        :param level: (currently unused)
        :type level: str
        :param old_node: reference to the node of the old property
        :type old_node: mdl.PropertyMode
        :param values: set of possible values for a picklist property
        :type values: tuple
        :rtype: None
        """
        new_node = mdl.PropertyNode(name=name, prop_type=prop_type,
                                    values=values)
        self._model.alter_node(old_node, new_node)
