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
.. currentmodule:: src.main

This module is the main entry point of the program, containing its main function
as well as the definition of the ``QApplication`` where the event loop is run.
"""

import logging.config
import sys

from PyQt4 import QtCore, QtGui

from src import model, controller, view


_CSS = 'style.qss'
"""Location of the application stylesheet (Qt StyleSheet).
"""


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
        # styles the application
        self._apply_style()
        # translates the application UI
        translator = QtCore.QTranslator()
        translator.load(':/l10n/{0}'.format(QtCore.QLocale.system().name()))
        self.installTranslator(translator)
        # creates the view
        self._view = view.MainWindow()
        # creates the controller
        self._controller = controller.MainController(self._view)
        # has the view drawn on the screen (finally)
        self._view.show()

    def _apply_style(self):
        """Applies the stylesheet to the whole application.

        :rtype: None
        """
        try:
            with open(_CSS, 'r') as file_handle:
                style = file_handle.read()
            self.setStyleSheet(style)
        except IOError as exc:
            print(exc.message)


# what to to when this module is executed as the main module (which it is)
if __name__ == '__main__':
    app = MetaTermApplication(sys.argv)
    sys.exit(app.exec())
