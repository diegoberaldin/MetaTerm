# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.controller.abstract

This module contains the base class for all the controllers that are used in
the application, which is the responsible of the event handling mechanisms.
"""

from PyQt4 import QtCore


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
