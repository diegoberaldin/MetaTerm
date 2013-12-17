# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.main

This module is the main entry point of the program, containing its main function
as well as the definition of the ``QApplication`` where the event loop is run.
"""

import logging.config
import sys
from PyQt4 import QtGui

from src import model, controller, view


def initialize_logging():
    """Initializes the logging module for use throughout the whole application,
    reading the configuration from the ``logging.conf`` file located at the same
    level as the main module.

    :rtype: None
    """
    logging.config.fileConfig('logging.conf')


class MetaTermApplication(QtGui.QApplication):
    """This is the application hosting the main event loop, directly inherited
    by the superclass and started when the exec() method is called.
    """

    def __init__(self, args):
        """Constructor method for the application.

        :param args: list of arguments from the command line
        :type args: list
        :rtype: MetaTermApplication
        """
        super(MetaTermApplication, self).__init__(args)
        # initializes logging
        initialize_logging()
        # initializes the termbase folder
        model.initialize_tb_folder()
        # creates the view
        self._view = view.MainWindow()
        # creates the controller
        self._controller = controller.MainController(self._view)
        # has the view drawn on the screen (finally)
        self._view.show()


# what to to when this module is executed as the main module (which it is)
if __name__ == '__main__':
    # 2 lines of plain old boilerplate code won't harm anybody
    app = MetaTermApplication(sys.argv)
    sys.exit(app.exec())
