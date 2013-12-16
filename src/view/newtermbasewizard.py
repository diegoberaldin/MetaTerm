# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.newtermbasewizard

This module contains the classes used to define the wizard that will guide the
user through the creation of a new terminological database.
"""

from PyQt4 import QtGui, QtCore


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
        self._pages = [NamePage(), LanguagePage(), DefinitionModelPage(),
                       FinalPage()]
        for page in self._pages:
            self.addPage(page)
            # signal-slot connections
        self.finished.connect(self._handle_finished)

    @QtCore.pyqtSlot()
    def _handle_finished(self):
        """This slot is activated when the user presses the 'finish' button of
        the wizard, it collects all the data that have either been stored in
        wizard fields or in page-specific structures and informs the controller
        about the event so that the termbase file can be created on disk.

        :rtype: None
        """
        pass


class NamePage(QtGui.QWizardPage):
    """This page allows the user to select the name of the new termbase that is
    being created.
    """

    def __init__(self):
        """Constructor method.

        :rtype: NamePage
        """
        super(NamePage, self).__init__()
        self.setTitle('Termbase name')
        self.setSubTitle(
            'This wizard will guide you through the creation of a new '
            'termbase. Please enter the name of the new termbase in the field'
            'below')
        self.setLayout(QtGui.QFormLayout(self))
        name_label = QtGui.QLabel('Name', self)
        name_input = QtGui.QLineEdit(self)
        self.layout().addRow(name_label, name_input)
        # field registration
        self.registerField('termbase_name*', name_input)


class LanguagePage(QtGui.QWizardPage):
    """This page allows the user to choose the languages of the terms that will
    be stored in the new termbase.
    """

    def __init__(self):
        """Constructor method.

        :rtype: LanguagePage
        """
        super(LanguagePage, self).__init__()
        self.setTitle('Termbase languages')
        self.setSubTitle(
            'Select the languages of the terms that will be stored in the new '
            'termbase.')
        self.setLayout(QtGui.QGridLayout(self))


class DefinitionModelPage(QtGui.QWizardPage):
    def __init__(self):
        """Constructor method.

        :rtype: DefinitionModelPage
        """
        super(DefinitionModelPage, self).__init__()
        self.setTitle('Definition model')
        self.setSubTitle(
            'Create the structure of the termbase by specifying the set of '
            'properties that its entries'
            'will be made up of')


class FinalPage(QtGui.QWizardPage):
    def __init__(self):
        """Constructor method.

        :rtype: FinalPage
        """
        super(FinalPage, self).__init__()
        self.setTitle('Congrats!')
        self.setSubTitle(
            'If you confirm the operation, the new termbase will be created.')