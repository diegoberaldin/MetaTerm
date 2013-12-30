# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.controller

This package contains the modules which the controller is made up of. Each one
of these modules is intended to contain a specific controller which may receive
notifications from more than one (possibly all) part of the GUI and processes
the events originating from there in order to accomplish some related tasks
interacting with some part (possibly more than one) of the application model.
"""

from src.controller.main import MainController
