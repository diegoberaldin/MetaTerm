# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.newtermbasewizard

This module contains the classes used to define the wizard that will guide the
user through the creation of a new terminological database.
"""

from PyQt4 import QtGui, QtCore
from src import model as mdl

PROP_TYPES = ['Text', 'Image', 'Picklist']
"""Type of the properties that must be displayed in the UI.
"""


class NewTermbaseWizard(QtGui.QWizard):
    """Main ``QWizard`` subclass used to implement the new termbase wizard.
    """

    def __init__(self, termbase_definition_model, parent):
        """Constructor method.

        :param termbase_definition_model: reference to the term definition model
        :type termbase_definition_model: TermbaseDefinitionModel
        :param parent: reference to the application main window
        :type parent: QtGui.QWidget
        :rtype: NewTermbaseWizard
        """
        super(NewTermbaseWizard, self).__init__(parent)
        # a reference to the termbase definition model
        self.termbase_definition_model = termbase_definition_model
        self.setWindowTitle('Create new termbase')
        self._pages = [NamePage(self), LanguagePage(self),
                       DefinitionModelPage(self),
                       FinalPage(self)]
        for page in self._pages:
            self.addPage(page)
        self.setVisible(True)
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

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the containing wizard
        :type parent: QtGui.QWidget
        :rtype: NamePage
        """
        super(NamePage, self).__init__(parent)
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

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the containing wizard
        :type parent: QtGui.QWidget
        :rtype: LanguagePage
        """
        super(LanguagePage, self).__init__(parent)
        self.setTitle('Termbase languages')
        self.setSubTitle(
            'Select the languages of the terms that will be stored in the new '
            'termbase.')
        self.setLayout(QtGui.QGridLayout(self))
        # creates the two QListWidgets
        self._available_languages = QtGui.QListWidget(self)
        self._chosen_languages = QtGui.QListWidget(self)
        self._populate_available_languages()
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

    def _populate_available_languages(self):
        """ Extracts the information about languages that is stored in the
        model (default languages) and populates the available languages
        QListView with the corresponding items.

        :rtype: None
        """
        for locale, language_name in mdl.DEFAULT_LANGUAGES.items():
            flag = QtGui.QIcon(':/flags/{0}.png'.format(locale))
            item = QtGui.QListWidgetItem(flag, language_name,
                                         self._available_languages)
            self._available_languages.addItem(item)
        self._available_languages.sortItems(QtCore.Qt.AscendingOrder)

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
        """Returns a list of all the language locales that have been selected
        this ``LanguagePage`` instance.

        :return: list of all selected locales
        :rtype: list
        """
        items = []
        while self._chosen_languages.count():
            items.append(self._chosen_languages.takeItem(0))
        items = [item.data(0) for item in items]
        # TODO: careful when new languages are added
        return [k for lang_name in items for k, v in
                mdl.DEFAULT_LANGUAGES.items() if v == lang_name]


class DefinitionModelPage(QtGui.QWizardPage):
    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the containing wizard
        :type parent: QtGui.QWidget
        :rtype: DefinitionModelPage
        """
        super(DefinitionModelPage, self).__init__(parent)
        self.setTitle('Definition model')
        self.setSubTitle(
            'Create the structure of the termbase by specifying the set of '
            'properties that its entries will be made up of')
        self.setLayout(QtGui.QHBoxLayout(self))
        self._view = QtGui.QTreeView(self)
        self._view.setModel(self.parent().termbase_definition_model)
        self._view.pressed.connect(self._handle_view_pressed)
        self._form = QtGui.QWidget(self)
        self._form.setMinimumWidth(250)
        self.layout().addWidget(self._view)
        self.layout().addWidget(self._form)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def _handle_view_pressed(self, index):
        """This slot must be activated when the tree view is clicked and has
        the responsibility of changing the right part of the wizard page in
        order to either add a new property (when a 'level node' is selected in
        the view) or modify an existing property (when a 'property node' is
        selected.

        :param index: the index being selected when the view is clicked
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        item = index.internalPointer()
        old_form = self._form
        self.layout().removeWidget(old_form)
        if not item.parent.parent:  # level node
            self._form = NewPropertyForm(self)

        else:  # modify existing property
            pass
        self._form.setMinimumWidth(250)
        self.layout().addWidget(self._form)
        old_form.deleteLater()


class NewPropertyForm(QtGui.QWidget):
    """Form used to create a new property in the termbase definition. The
    property must be added within the level that has been selected in the tree
    view at the moment property creation was started.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the wizard page containing this form
        :type parent: QtCore.QWidget
        :rtype: NewPropertyForm
        """
        super(NewPropertyForm, self).__init__(parent)
        # form fields
        name_label = QtGui.QLabel('Name', self)
        self._name_input = QtGui.QLineEdit(self)
        type_label = QtGui.QLabel('Type', self)
        type_input = QtGui.QComboBox(self)
        type_input.setModel(
            QtGui.QStringListModel(PROP_TYPES))
        type_input.currentIndexChanged.connect(self._handle_type_changed)
        # subwidget corresponding to the 'toolbar'
        add_widget = QtGui.QWidget(self)
        add_widget.setLayout(QtGui.QHBoxLayout(add_widget))
        add_button = QtGui.QToolButton(add_widget)
        add_button.setText('Add property')
        add_button.setIcon(QtGui.QIcon(':/list-add.png'))
        add_widget.layout().addStretch()
        add_widget.layout().addWidget(add_button)
        self._value_label = None
        self._value_input = None
        # puts it all together
        self.setLayout(QtGui.QFormLayout(self))
        self.layout().addWidget(add_widget)
        self.layout().addRow(name_label, self._name_input)
        self.layout().addRow(type_label, type_input)
        self.layout().addRow(self._value_label, self._value_input)


    @QtCore.pyqtSlot(int)
    def _handle_type_changed(self, type_index):
        """This slot has the responsibility of changing the form contents
        depending on the type of property that has been selected. If a non-
        picklist property is selected, only the name of the property must be
        entered, whereas if a picklist property is being created, the set of
        possible values must be specified too.

        :param type_index: integer corresponding to the index of the property
        type as it is found in the PROP_TYPE module constant.
        :type type_index: int
        :rtype: None
        """
        if self._value_input and self._value_label:
            self.layout().removeWidget(self._value_input)
            self.layout().removeWidget(self._value_label)
            self._value_input.deleteLater()
            self._value_label.deleteLater()
        if type_index == 2:  # picklist property
            self._value_label = QtGui.QLabel('Values')
            self._value_input = QtGui.QLabel('picklist', self)
            self.layout().addRow(self._value_label, self._value_input)
        else:
            self._value_label = None
            self._value_input = None


class FinalPage(QtGui.QWizardPage):
    def __init__(self, parent):
        """Constructor method.

        :rtype: FinalPage
        """
        super(FinalPage, self).__init__(parent)
        self.setTitle('Congrats!')
        self.setSubTitle(
            'If you confirm the operation, the new termbase will be created.')