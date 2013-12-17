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


class AbstractController(QtCore.QObject):
    """This is a convenience class that contains the generic event handler
    (namely the ``handle_event`` method) which all controllers must implement
    in order to be able to react to events originated in the GUI.
    """

    def __init__(self):
        """Constructor method (to be called in subclass constructors).

        :rtype AbstractController:
        """
        super(AbstractController, self).__init__()

    @QtCore.pyqtSlot(str, dict)
    def handle_event(self, event_name, params):
        """Generic event handler which must be provided by every controller: it
        has the responsibility of capturing UI events and forwarding their call
        to a more specific handler method (within this same class) after
        unpacking its arguments to a more readable form.

        :param event_name: name of the event to be handled
        :type event_name: str
        :param params: dictionary containing the handler parameters
        :rtype: None
        """
        method_name = '_handle_{0}'.format(event_name)
        if hasattr(self, method_name):
            try:  # this is the first and last little bit of black magic
                getattr(self, method_name)(**params)
            except TypeError as exc:  # incorrect parameters
                pass


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

    def _handle_open_termbase(self, termbase_name):
        """Opens an existing termbase.

        :param termbase_name: the name of the termbase to open
        :type termbase_name: str
        :rtype: None
        """
        self._model = mdl.TermBase(termbase_name)
        # TODO: UI must be updated

    def _handle_new_termbase(self):
        """Starts the wizard used to create a new termbase.

        :rtype: None
        """
        termbase_definition_model = mdl.TermbaseDefinitionModel()
        wizard = gui.NewTermbaseWizard(termbase_definition_model, self._view)
        new_termbase_controller = NewTermbaseController(
            termbase_definition_model, wizard)
        new_termbase_controller.new_termbase_created.connect(
            self._handle_open_termbase)
        self._children['new_termbase'] = new_termbase_controller
        wizard.setVisible(True)


class NewTermbaseController(AbstractController):
    new_termbase_created = QtCore.pyqtSignal(str)
    ('Signal emitted when a new termbase has been created. The name of the '
     'newly created termbase must be passed as a parameter when the signal'
     'is emitted.')

    def __init__(self, model, wizard):
        super(NewTermbaseController, self).__init__()
        self._view = wizard
        self._model = model

