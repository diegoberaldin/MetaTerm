# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.newtermbasewizard

This module contains the classes used to define the wizard that will guide the user through the creation of a new
terminological database.
"""

from PyQt4 import QtGui


class NewTermbaseWizard(QtGui.QWizard):
    """Main ``QWizard`` subclass used to implement the new termbase wizard.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the application main window
        :type parent: QWidget
        :rtype: NewTermbaseWizard
        """
        super(NewTermbaseWizard, self).__init__(parent)
        self.setWindowTitle('Create new termbase')
        self.addPage(FirstPage(self))


class FirstPage(QtGui.QWizardPage):
    """In the first page of the wizard the user can select the name of the new termbase and the languages involved.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the new termbase wizard
        :type parent: NewTermbaseWizard
        :rtype: FirstPage
        """
        super(FirstPage, self).__init__(parent)
        self.setTitle('Name and languages')
        self.setSubTitle('Select the name of the new termbase and the language of the terms that will be stored in it.')
        self.setLayout(QtGui.QFormLayout(self))
        name_label = QtGui.QLabel('Name', self)
        name_input = QtGui.QLineEdit(self)
        self.layout().addRow(name_label, name_input)
        # field registration
        self.registerField('termbase_name*', name_input)
