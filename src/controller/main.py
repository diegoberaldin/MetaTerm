# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.controller.maincontroller

This module contains the main application controller, i.e. the controller that
is directly bound to the main window of the application and is in charge of
processing all those events that are generated there.
"""

import os

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
        entry_view.model = entry_model
        # creates child controller
        entry_controller = EntryController(entry_model, entry_view)

    def _handle_new_termbase(self):
        """Starts the wizard used to create a new termbase.

        :rtype: None
        """
        # instantiates the model
        termbase_definition_model = mdl.TermbaseDefinitionModel()
        # creates the view
        wizard = gui.NewTermbaseWizard(termbase_definition_model, self._view)
        # creates the controller
        new_termbase_controller = NewTermbaseController(
            termbase_definition_model, wizard)
        # signal-slot connection
        wizard.accepted.connect(
            lambda: self._handle_open_termbase(wizard.field('termbase_name')))

    def _handle_close_termbase(self):
        """Closes the currently open termbase.

        :rtype: None
        """
        mdl.get_main_model().open_termbase = None
        self._view.display_message('Current termbase closed.')

    def _handle_delete_termbase(self, name):
        """Permanently deletes a termbase from disk.

        :param name: name of the termbase to be deleted
        :type name: str
        :rtype: None
        """
        if self._model and self._model.name == name:
            self._handle_close_termbase()
        file_name = mdl.Termbase(name).get_termbase_file_name()
        print(file_name)
        if os.path.exists(file_name):
            os.remove(file_name)
            self._view.display_message(
                'Termbase {0} has been deleted.'.format(name))
