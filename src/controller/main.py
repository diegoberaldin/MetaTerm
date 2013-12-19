# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.controller.maincontroller

This module contains the main application controller, i.e. the controller that
is directly bound to the main window of the application and is in charge of
processing all those events that are generated there.
"""

from PyQt4 import QtCore

from src import model as mdl
from src import view as gui
from src.controller.abstract import AbstractController
from src.controller.newtermbase import NewTermbaseController


class MainController(AbstractController):
    """This controller is responsible of handling the events that are generated
    either in the application main window
    or in the main widget that is displayed inside it.
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
        self._model = None
        # child controllers
        self._children = {}

    def _handle_open_termbase(self, name):
        """Opens an existing termbase.

        :param name: the name of the termbase to open
        :type name: str
        :rtype: None
        """
        self._model = mdl.Termbase(name)
        # TODO: UI must be updated

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
        # signal-slot connections
        new_termbase_controller.new_termbase_created.connect(
            self._handle_open_termbase)
