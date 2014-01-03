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
.. currentmodule:: src.controller.abstract

This module contains the base class for all the controllers that are used in
the application, which is the responsible of the event handling mechanisms.

Subclasses of this controller inherit the generic handler (``handle_event``
method) and must provide more specific handlers as instance methods, in the form
of ``_handle_[EVENT_NAME]`` where ``[EVENT_NAME]`` must be changed according to
the name of the specific event being handled.
"""

from PyQt4 import QtCore
import logging

# reference to the logger for the controller package
_LOG = logging.getLogger('src.controller')


class AbstractController(QtCore.QObject):
    """This is a convenience class that contains the generic event handler
    (namely the ``handle_event`` method) which all controllers must implement
    in order to be able to react to events originated in the GUI.
    """

    finished = QtCore.pyqtSignal()
    """Signal emitted by all controllers when they have finished their work.
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
                _LOG.exception(exc)
