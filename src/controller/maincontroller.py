"""
.. currentmodule:: src.controller.maincontroller

This module contains the main application controller, i.e. the controller that is directly bound to the main window
of the application and is in charge of processing all those events that are generated there.
"""

from PyQt4 import QtCore


class AbstractController(QtCore.QObject):
    """This is a convenience class that contains the generic event handler (namely the ``handle_event`` method) which
    all controllers must implement in order to be able to react to events originated in the GUI.
    """
    def __init__(self):
        """Constructor method (to be called in subclass constructors).

        :rtype AbstractController:
        """
        super(AbstractController, self).__init__()

    @QtCore.pyqtSlot(str, dict)
    def handle_event(self, event_name, params):
        """Generic event handler which must be provided by every controller: it has the responsibility of capturing
        UI events and forwarding their call to a more specific handler method (within this same class) after unpacking
        its arguments to a more readable form.

        :param event_name: name of the event to be handled
        :type event_name: str
        :param params: a dictionary containing the parameters required by the handler
        :rtype: None
        """
        method_name = '_handle_{0}'.format(event_name)
        if hasattr(self, method_name):
            try:  # this is the first and last little bit of black magic, I promise!
                getattr(self, method_name)(**params)
            except TypeError as exc:  # incorrect parameters
                pass


class MainController(AbstractController):
    """This controller is responsible of handling the events that are generated either in the application main window
    or in the main widget that is displayed inside it.
    """

    def __init__(self, view):
        """Constructor method.

        :param view: reference to the application main window
        :rtype: MainController
        """
        super(MainController, self).__init__()
        self._view = view
        self._view.fire_event.connect(self.handle_event)
