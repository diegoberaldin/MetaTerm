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
                print(exc)


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


class NewTermbaseController(AbstractController):
    """This controller is associated with the new termbase wizard and is
    responsible of keeping the termbase definition model up-to-date with the
    modification requested by the user to the termbase structure, as well as
    processing the data entered by the user when they confirm that a new
    termbase must be created.
    """
    new_termbase_created = QtCore.pyqtSignal(str)
    """Signal emitted when a new termbase has been created. The name of the
     newly created termbase must be passed as a parameter when the signal
     is emitted."""

    wizard_canceled = QtCore.pyqtSignal()
    """Signal emitted whenever the uses exits the wizard abnormally (this is
    needed by the main controller to deallocate its child controller).
    """

    def __init__(self, model, wizard):
        """Constructor

        :param model: reference to the model
        :type model: mdl.TermbaseDefinitionModel
        :param wizard: reference to the graphical user interface
        :type wizard: gui.NewTermbaseWizard
        :rtype: NewTermbaseController
        """
        super(NewTermbaseController, self).__init__()
        self._view = wizard
        self._view.rejected.connect(lambda: self.wizard_canceled.emit())
        self._view.accepted.connect(self._handle_termbase_created)
        self._view.fire_event.connect(self.handle_event)
        self._model = model

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
        self.new_termbase_created.emit(termbase_name)

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
        pass

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
