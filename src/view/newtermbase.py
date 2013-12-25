# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.newtermbase

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

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted so that events can be handled by the controller.
    """

    MINIMUM_WIDTH = 500
    """Minimum width of the wizard window.
    """

    MINIMUM_HEIGHT = 400
    """Minimum height of the wizard window.
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
        self._pages[2].fire_event.connect(self.fire_event)
        self.setMinimumSize(self.MINIMUM_WIDTH, self.MINIMUM_HEIGHT)
        self.setVisible(True)

    def accept(self):
        self.fire_event.emit('termbase_created', {})
        super(NewTermbaseWizard, self).accept()

    def get_termbase_name(self):
        """Returns the name of the new termbase chosen by the user.

        :returns: the name of the new termbase
        :rtype: str
        """
        return self.field('termbase_name')

    def get_termbase_locales(self):
        """Extracts the list of the selected languages (locale strings, to be
        used as keys in the ``DEFAULT_LANGUAGES`` dictionary) for the new TB.

        :returns: a list of the locales that have been selected by the user
        :rtype: list
        """
        language_page = self._pages[1]
        return language_page.get_selected_locales()


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

    def validatePage(self):
        """Overridden in order to avoid name conflicts in the termbases, it
        checks whether a termbase with the same name exists in the termbase
        directory of the local system and returns False (page is invalid) in
        the latter case, True otherwise. Moreover, it shows a warning message
        to inform the user about the problem.

        :return: True is the termbase name is not a duplicate, False otherwise
        :rtype: bool
        """
        tb_name = '{0}.sqlite'.format(self.field('termbase_name'))
        if tb_name in mdl.get_termbase_names():
            QtGui.QMessageBox.warning(self, 'Name conflict',
                                      'A termbase with the same name already '
                                      'exists on the system, please choose a '
                                      'different one.')
            return False
        return True


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
    """This page allows users to define the structure of the termbase by
    specifying the properties that will be applied to entries, languages and
    terms and, in case of picklist properties, the set of acceptable values.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to dispatch event to the controller.
    """

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
        self._view = QtGui.QTreeView(self)
        self._model = self.parent().termbase_definition_model
        self._view.setModel(self._model)
        self._view.pressed.connect(self._handle_view_pressed)
        self._form = QtGui.QWidget(self)
        # puts everything together
        self._splitter = QtGui.QSplitter(self)
        self._splitter.addWidget(self._view)
        self._splitter.addWidget(self._form)
        self._splitter.setSizes([200, 300])
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self._splitter)

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
            self._form = ChangePropertyForm(item, self)
        self._form.fire_event.connect(self.fire_event)
        self._form.setMinimumWidth(250)
        self._splitter.addWidget(self._form)
        old_form.deleteLater()

    def get_level(self):
        """Returns a string in ``['E', 'L', 'T']`` corresponding to the level
        where a newly created property must be inserted in the TDM.

        :return: a single-character string representing the level where the
        new property must be inserted
        :rtype: str
        """
        item = [index.internalPointer() for index in
                self._view.selectedIndexes() if index.column() == 0].pop()
        index = item.parent.children.index(item)
        if index == 0:
            return 'E'
        if index == 1:
            return 'L'
        return 'T'

    def isComplete(self):
        """Overridden in order to ensure that at least one property has been
        defined in the termbase definition model.

        :return: True if some property has been defined, False otherwise
        :rtype: bool
        """
        return self._model.get_property_number() != 0

    def reset_all(self):
        """Redraws the correct form in the page based on the current selection.

        :rtype: None
        """
        selected_indexes = [index for index in
                            self._view.selectedIndexes() if
                            index.column() == 0]
        if selected_indexes:
            current_index = selected_indexes.pop()
            self._view.pressed.emit(current_index)


class AlterPropertyForm(QtGui.QWidget):
    """Base class for those forms having the purpose of creating or updating a
    property in the termbase definition model. These forms share some common
    fields such as the property name and type, plus a toolbar allowing the
    changes to be reflected in the underlying termbase definition model.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to dispatch event to the controller.
    """

    def __init__(self, page, parent):
        """Constructor method

        :param parent: reference to the widget parent
        :type parent: QtGui.QWidget
        :param page: reference to the container wizard page
        :type page: QtGui.QWizardPage
        :rtype: AlterPropertyForm
        """
        super(AlterPropertyForm, self).__init__(parent)
        self.setLayout(QtGui.QFormLayout(self))
        self._page = page
        self._name_input = None
        self._type_input = None
        self._value_label = None
        self._value_input = None
        self._create_toolbar()
        self._create_form_fields()

    def _create_toolbar(self):
        """Hook method used to create the toolbar which will be displayed in
        the upper part of the form.

        :rtype: None
        """
        raise NotImplementedError('Implement me!')

    def clear(self):
        """Completely clears the form, which loses any information that has
        been inserted in it.

        :rtype: None
        """
        if self._value_label:
            self.layout().removeWidget(self._value_label)
            self._value_label.deleteLater()
        if self._value_input:
            self.layout().removeWidget(self._value_input)
            self._value_input.deleteLater()
        self._value_input = None
        self._value_label = None
        self._name_input.clear()
        self._type_input.setCurrentIndex(0)

    def _create_form_fields(self):
        """Creates the fields which are shared by all forms (i.e. a field for
        the property name and one for the property type).

        :rtype: None
        """
        name_label = QtGui.QLabel('Name', self)
        self._name_input = QtGui.QLineEdit(self)
        type_label = QtGui.QLabel('Type', self)
        self._type_input = QtGui.QComboBox(self)
        self._type_input.setModel(
            QtGui.QStringListModel(PROP_TYPES))
        self._type_input.currentIndexChanged.connect(self._handle_type_changed)
        self.layout().addRow(name_label, self._name_input)
        self.layout().addRow(type_label, self._type_input)

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
            self._value_label = QtGui.QLabel('Values', self)
            self._value_input = PicklistEditor(self)
            self.layout().addRow(self._value_label, self._value_input)
        else:
            self._value_label = None
            self._value_input = None

    def extract_property_data(self):
        """Extracts the information about the new property from the form.

        :returns: a dictionary with the ``name``, ``level``, ``prop_type`` and
        ``values`` keys representing the information about the property to be
        added to the termbase definition model
        :rtype: dict
        """
        property_data = {
            'name': self._name_input.text(),
            'level': self._page.get_level()
        }
        if self._type_input.currentIndex() == 0:
            property_data['prop_type'] = 'T'
        elif self._type_input.currentIndex() == 1:
            property_data['prop_type'] = 'I'
        else:
            property_data['prop_type'] = 'P'
            property_data['values'] = self._value_input.values
        return property_data

    def is_complete(self):
        """Determines whether the information in the form is enough to define
        a new property. For text and image based properties the simple name of
        the property suffices, whereas in case of picklist properties at least
        one item must be specified in the set of possible values.

        :returns: True if all the required fields have been filled in correctly,
        False otherwise
        :rtype: bool
        """
        if self._name_input:
            if self._type_input.currentIndex() == 2:
                if self._value_input.values:
                    return True
            else:
                return True
        return False


class NewPropertyForm(AlterPropertyForm):
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
        super(NewPropertyForm, self).__init__(parent, parent)

    def _create_toolbar(self):
        """Overridden in order to create a toolbar with an 'add property' tool
        button used to create the new property and inserting it in the
        underlying termbase definition model.
        """
        toolbar = QtGui.QWidget(self)
        toolbar.setLayout(QtGui.QHBoxLayout(toolbar))
        add_button = QtGui.QToolButton(toolbar)
        add_button.setText('Add property')
        add_button.setIcon(QtGui.QIcon(':/document-new.png'))
        add_button.clicked.connect(self._handle_add_property)
        toolbar.layout().addStretch()
        toolbar.layout().addWidget(add_button)
        self.layout().addWidget(toolbar)

    @QtCore.pyqtSlot()
    def _handle_add_property(self):
        if self.is_complete():
            self.fire_event.emit('new_property',
                                 self.extract_property_data())
            self.clear()
            # notifies the wizard page that a property has been added
            self._page.completeChanged.emit()


class ChangePropertyForm(AlterPropertyForm):
    """This form is used to change the name, type or possible picklist values
    of an existing property, as well as reflecting those changes in the model.
    """

    def __init__(self, prop, parent):
        """Constructor method.

        :param prop: the property being edited
        :type prop: PropertyNode
        :param parent: reference to the wizard page containing this form
        :type parent: QtCore.QWidget
        :rtype: ChangePropertyForm
        """
        self._property = prop  # used in constructor hook
        super(ChangePropertyForm, self).__init__(parent, parent)

    def _create_form_fields(self):
        super(ChangePropertyForm, self)._create_form_fields()
        self._name_input.setText(self._property.name)
        if self._property.type == 'T':
            self._type_input.setCurrentIndex(0)
        elif self._property.type == 'I':
            self._type_input.setCurrentIndex(1)
        else:
            self._type_input.setCurrentIndex(2)

    def _handle_type_changed(self, type_index):
        """This is overridden because when the form fields are initialized the
        index is changed programmatically so this slot is invoked and it needs
        to add the correct values in the list view.

        :param type_index: index of the property type combobox
        :type type_index: int
        :rtype: None
        """
        super(ChangePropertyForm, self)._handle_type_changed(type_index)
        if type_index == 2:
            for value in self._property.values:
                self._value_input.insert_value(value)

    def _create_toolbar(self):
        """Overridden in order to create a toolbar with an 'save property' tool
        button used to update existing property with the latest changes.

        :rtype: None
        """
        toolbar = QtGui.QWidget(self)
        toolbar.setLayout(QtGui.QHBoxLayout(toolbar))
        save_button = QtGui.QToolButton(toolbar)
        save_button.setText('Save property')
        save_button.setIcon(QtGui.QIcon(':/document-save.png'))
        save_button.clicked.connect(self._handle_change_property)
        delete_button = QtGui.QToolButton(toolbar)
        delete_button.setText('Delete property')
        delete_button.setIcon(QtGui.QIcon(':/document-close.png'))
        delete_button.clicked.connect(self._handle_delete_property)
        toolbar.layout().addStretch()
        toolbar.layout().addWidget(delete_button)
        toolbar.layout().addWidget(save_button)
        self.layout().addWidget(toolbar)

    @QtCore.pyqtSlot()
    def _handle_change_property(self):
        """This slot is activated when a property needs to be changed, it simply
        emits a signal which the controller listen to in order to modify the
        termbase definition model data structure.

        :rtype: None
        """
        if self.is_complete():
            prop_data = self.extract_property_data()
            prop_data['old_node'] = self._property
            self.fire_event.emit('change_property', prop_data)
            # puts the form back in a consistent state (_property reference)
            self._page.reset_all()

    @QtCore.pyqtSlot()
    def _handle_delete_property(self):
        """This slot is activated whenever a property needs to be deleted. It
        dispatches an event so that the controller can carry out the operation.

        :rtype: None
        """
        self.fire_event.emit('delete_property', {'old_node': self._property})
        # notifies the wizard page that a property has been deleted
        self._page.completeChanged.emit()
        # completely clears the form
        self._page.reset_all()


class PicklistEditor(QtGui.QWidget):
    """Graphical widget used to create and manage picklists by adding or
    removing values to the range of possible values.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: parent of the widget
        :type parent: QtGui.QWidget
        :rtype: PicklistEditor
        """
        super(PicklistEditor, self).__init__(parent)
        self.values = []
        # widget to insert the new value
        self._value_input = QtGui.QLineEdit(self)
        self._value_input.setMinimumHeight(20)
        value_widget = QtGui.QWidget(self)
        value_widget.setLayout(QtGui.QGridLayout(value_widget))
        value_widget.layout().addWidget(self._value_input, 0, 0)
        add_button = QtGui.QToolButton(value_widget)
        add_button.setIcon(QtGui.QIcon(':/list-add.png'))
        add_button.setText('Append to picklist')
        add_button.setMinimumHeight(20)
        add_button.clicked.connect(self._handle_new_value)
        value_widget.layout().addWidget(add_button, 0, 1)
        # list view where possible values are displayed
        self._list_view = QtGui.QListWidget(self)
        self._list_view.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(value_widget)
        self.layout().addWidget(self._list_view)

    def insert_value(self, value):
        """Inserts a new value in the picklist editor so that it is displayed
        in the list widget and it is accessible to subsequent save operations.

        :param value: the new item to add to the picklist value set
        :type value: str
        :rtype: None
        """
        self.values.append(value)
        item = QtGui.QListWidgetItem()
        widget = PicklistValueWidget(value, self)
        widget.removed.connect(self._handle_remove_value)
        item.setSizeHint(QtCore.QSize(50, 30))
        index = self._list_view.count()
        self._list_view.insertItem(index, item)
        self._list_view.setItemWidget(item, widget)

    @QtCore.pyqtSlot()
    def _handle_new_value(self):
        """This slot is activated whenever a new value needs to be inserted
        in the set of possible values for a picklist property, based on the
        value of the line edit contained within the picklist editor itself.

        :rtype: None
        """
        text = self._value_input.text()
        self.insert_value(text)
        self._value_input.clear()

    @QtCore.pyqtSlot(str)
    def _handle_remove_value(self, value):
        """This slot is activated when the given value needs to be removed from
        the set of possible values for a picklist property. It will also remove
        the corresponding item widget (``PicklistValueWidget``) from the
        list view where the current values are shown.

        :param value: the value to be removed
        :type value: str
        :rtype: None
        """
        index = 0
        while index < self._list_view.count():
            item = self._list_view.item(index)
            widget = self._list_view.itemWidget(item)
            if widget.value == value:
                break
            index += 1
        self._list_view.takeItem(index)
        self.values.remove(value)


class PicklistValueWidget(QtGui.QWidget):
    """Instances of this class are used to represent those graphical widget
    that are inserted in the ``PicklistEditor`` internal tree view in order
    to represent the possible values of a picklist property. Each item widget
    must display the value of the property inside a label and contains a
    button used to remove the value from the set of acceptable values.
    """
    removed = QtCore.pyqtSignal(str)
    """Signal emitted when the user asks to remove the item from the set.
    """

    def __init__(self, value, parent):
        """Constructor method.

        :param value: representation of the value to add
        :type value: str
        :param parent: reference to the widget parent
        :type parent: QtCore.QWidget
        :rtype: PicklistValueWidget
        """
        super(PicklistValueWidget, self).__init__(parent)
        self.value = value
        self.setLayout(QtGui.QHBoxLayout(self))
        self.layout().addWidget(QtGui.QLabel(value, self))
        remove_button = QtGui.QToolButton(self)
        remove_button.setIcon(QtGui.QIcon(':/list-remove.png'))
        self.layout().addWidget(remove_button)
        remove_button.clicked.connect(lambda: self.removed.emit(value))


class FinalPage(QtGui.QWizardPage):
    def __init__(self, parent):
        """Constructor method.

        :rtype: FinalPage
        """
        super(FinalPage, self).__init__(parent)
        self.setTitle('Congrats!')
        self.setSubTitle(
            'If you confirm the operation, the new termbase will be created.')
