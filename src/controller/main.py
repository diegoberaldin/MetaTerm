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
.. currentmodule:: src.controller.maincontroller

This module contains the main application controller, i.e. the controller that
is directly bound to the main window of the application and is in charge of
processing all those events that are generated there.
"""

import os

from PyQt4 import QtCore
from src import model as mdl
from src import view as gui
from src.controller.abstract import AbstractController
from src.controller.newtermbase import NewTermbaseController
from src.controller.entry import EntryController


class MainController(AbstractController):
    """This controller is responsible of handling the events that are generated
    either in the application main window or in the main widget that is
    displayed inside it.
    """

    def __init__(self, view):
        """Constructor method.

        :param view: reference to the application main window
        :rtype: MainController
        """
        super(MainController, self).__init__()
        self._view = view
        # assures events originated from the UI are handled correctly
        self._view.fire_event.connect(self.handle_event)
        # child controllers
        self._children = {}

    def _handle_open_termbase(self, name):
        """Opens an existing termbase.

        :param name: the name of the termbase to open
        :type name: str
        :rtype: None
        """
        # creates a termbase and saves it in the main application model
        termbase = mdl.Termbase(name)
        mdl.get_main_model().open_termbase = termbase
        # prints a message in the view
        self._view.display_message('Currently working on {0}'.format(name))
        # creates an entry model
        entry_model = mdl.EntryModel(termbase)
        # initializes the entry-specific part of the view with the entry model
        entry_view = self._view.centralWidget()
        entry_view.entry_model = entry_model
        # creates child controller
        self._children['entry'] = EntryController(entry_model, entry_view)
        # signal-slot connections
        self._view.fire_event.connect(self._children['entry'].handle_event)

    def _handle_new_termbase(self):
        """Starts the wizard used to create a new termbase.

        :rtype: None
        """
        # instantiates the model
        termbase_definition_model = mdl.TermbaseDefinitionModel()
        # creates the view
        wizard = gui.NewTermbaseWizard(termbase_definition_model, self._view)
        # creates the controller
        self._children['new_termbase'] = NewTermbaseController(
            termbase_definition_model, wizard)
        # signal-slot connection
        self._children['new_termbase'].finished.connect(
            lambda: self._finalize_child_controller('new_termbase'))
        wizard.accepted.connect(
            lambda: self._handle_open_termbase(wizard.field('termbase_name')))

    @QtCore.pyqtSlot(str)
    def _finalize_child_controller(self, child_name):
        """This slot is used as a means by the main controller to observe its
        child controllers and safely delete (causing them to be garbage
        collected) them when they inform it that they are done with their tasks.

        :param child_name: key to be used in the children dictionary
        :type child_name: str
        :rtype: None
        """
        del self._children[child_name]

    def _handle_close_termbase(self):
        """Closes the currently open termbase.

        :rtype: None
        """
        mdl.get_main_model().open_termbase = None
        self._view.display_message('Current termbase closed.')
        self._children['entry'].finished.emit()

    def _handle_delete_termbase(self, name):
        """Permanently deletes a termbase from disk.

        :param name: name of the termbase to be deleted
        :type name: str
        :rtype: None
        """
        model = mdl.get_main_model().open_termbase
        if model and model.name == name:
            self._handle_close_termbase()
        file_name = mdl.Termbase(name).get_termbase_file_name()
        if os.path.exists(file_name):
            os.remove(file_name)
            self._view.display_message(
                'Termbase {0} has been deleted.'.format(name))

    def _handle_entry_changed(self):
        """When the content of an entry manipulator form gets changed, the
        current entry can be saved so this event handler activates the
        corresponding action in the main view.

        :rtype: None
        """
        self._view.save_entry_action.setEnabled(True)

    def _handle_entry_displayed(self):
        """When an entry is displayed in the entry view, that entry can be
        edited or deleted, so this event handler activates the corresponding
        actions in the main view.

        :rtype: None
        """
        self._view.edit_entry_action.setEnabled(True)
        self._view.delete_entry_action.setEnabled(True)
        self._view.cancel_edit_action.setEnabled(False)

    def _handle_ui_reset(self):
        """When the UI is reset no entry can be manipulated, so this event
        handler prevents the entry manipulation actions from being triggered.

        :rtype: None
        """
        self._view.save_entry_action.setEnabled(False)
        self._view.edit_entry_action.setEnabled(False)
        self._view.delete_entry_action.setEnabled(False)
        self._view.cancel_edit_action.setEnabled(False)
