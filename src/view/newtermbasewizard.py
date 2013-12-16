# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.newtermbasewizard

This module contains the classes used to define the wizard that will guide the
user through the creation of a new terminological database.
"""

from PyQt4 import QtGui, QtCore
from src import model as mdl


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
        language_page = self._pages[1]
        print(language_page.get_selected_locales())


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
        self._available_languages = QtGui.QListWidget(self)
        for locale, language_name in mdl.DEFAULT_LANGUAGES.items():
            flag = QtGui.QIcon(':/flags/{0}'.format(locale))
            item = QtGui.QListWidgetItem(flag, language_name,
                                         self._available_languages)
            self._available_languages.addItem(item)
        self._available_languages.sortItems(QtCore.Qt.AscendingOrder)
        self._chosen_languages = QtGui.QListWidget(self)
        # buttons for moving languages around
        button_widget = QtGui.QWidget(self)
        select_language_button = QtGui.QPushButton('>', button_widget)
        select_language_button.setMaximumWidth(40)
        select_language_button.clicked.connect(self._handle_language_selected)
        deselect_language_button = QtGui.QPushButton('<', button_widget)
        deselect_language_button.setMaximumWidth(40)
        deselect_language_button.clicked.connect(
            self._handle_language_deselected)
        button_widget.setLayout(QtGui.QVBoxLayout(button_widget))
        button_widget.layout().addWidget(select_language_button)
        button_widget.layout().addWidget(deselect_language_button)
        # puts it all together
        self.layout().addWidget(self._available_languages, 0, 0)
        self.layout().addWidget(button_widget, 0, 1)
        self.layout().addWidget(self._chosen_languages, 0, 2)

    @QtCore.pyqtSlot()
    def _handle_language_selected(self):
        """This slot removes the selected item from the list of available
        languages and inserts in in the list of the selected languages.

        :rtype: None
        """
        index = self._available_languages.currentRow()
        item = self._available_languages.takeItem(index)
        self._chosen_languages.addItem(item)
        self._chosen_languages.sortItems(QtCore.Qt.AscendingOrder)
        self.completeChanged.emit()

    @QtCore.pyqtSlot()
    def _handle_language_deselected(self):
        """This slot removes the selected item from the list of the chosen
        languages and reinserts it in the list of available languages.

        :rtype: None
        """
        index = self._chosen_languages.currentRow()
        item = self._chosen_languages.takeItem(index)
        self._available_languages.addItem(item)
        self._available_languages.sortItems(QtCore.Qt.AscendingOrder)
        self.completeChanged.emit()

    def isComplete(self):
        """This method is overridden in order not to enable the 'Next' button
        unless at least one language has been selected by the user.

        :return: True if the page is complete and at least one language has
        been selected; False otherwise
        :rtype: bool
        """
        some_language_selected = self._chosen_languages.count() != 0
        return super(LanguagePage, self).isComplete() and some_language_selected

    def get_selected_locales(self):
        items = []
        while self._chosen_languages.count():
            items.append(self._chosen_languages.takeItem(0))
        items = [item.data(0) for item in items]
        # TODO: careful when new languages are added
        return [k for lang_name in items for k, v in
                mdl.DEFAULT_LANGUAGES.items() if v == lang_name]


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