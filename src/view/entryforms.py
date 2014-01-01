# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entryforms

This module contains the definition of the forms that are used in order to
create new terminological entries or to modify existing ones.
"""

import os

from PyQt4 import QtCore, QtGui

from src import model as mdl


class SelectFileInput(QtGui.QWidget):
    """Input widget used to select a resource from the local file system which
    basically consists of a disabled text field where the path is displayed
    and a browsing button. When the latter is clicked a dialog is opened to
    pick a resource from the local file system.
    """

    path_changed = QtCore.pyqtSignal()
    """Signal emitted when the path of the selected resource has changed.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtCore.QWidget
        :rtype: SelectFileInput
        """
        super(SelectFileInput, self).__init__(parent)
        self.setLayout(QtGui.QHBoxLayout(self))
        self._text_input = QtGui.QLineEdit(self)
        self._text_input.setEnabled(False)
        browse_button = QtGui.QPushButton('Browse', self)
        browse_button.clicked.connect(self._handle_button_clicked)
        self.layout().addWidget(self._text_input)
        self.layout().addWidget(browse_button)

    @QtCore.pyqtSlot()
    def _handle_button_clicked(self):
        """Private slot to be called when the button is clicked, after asking
        the user for a path to a local resource this is shown in the text
        input field and the ``path_changed`` signal is emitted.

        :rtype: None
        """
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose file',
                                                      os.path.expanduser('~'))
        if file_path:
            self._text_input.setText(file_path)
        else:
            self._text_input.setText('')
        self.path_changed.emit()

    @property
    def value(self):
        """Allows for subsequent form fields to access the selected value, i.e.
        the path that is shown in the text input field of the widget.

        :return: the selected (absolute) path to the resource
        :rtype: str
        """
        return self._text_input.text()

    @value.setter
    def value(self, value):
        self._text_input.setText(value)


class AbstractFormField(object):
    """This class is used as an abstraction mechanism for all the fields that
    are displayed in the form for the creation of a new terminological entry, no
    matter whether they are implemented using custom or library classes.

    Fields are characterized by the defined property the locale (which is
    needed for language-level and term-level properties) and the defined lemma,
    moreover they hold a reference to the graphical widget used to collect the
    user input needed for their definition.

    All such fields must implement the ``value`` property, allowing a caller
    to access the value of the property that has been specified by the user
    through the GUI.
    """

    def __init__(self, prop, level, widget, locale, lemma):
        """Constructor method.

        :param prop: reference to the property to be defined
        :type prop: Property
        :param level: level of the defined property
        :type level: str
        :param widget: reference to the graphical input widget
        :type widget: QtGui.QWidget
        :param locale: representation of the locale of the language
        :type locale: str
        :param lemma: lemma of the defined term
        :type lemma: str
        :rtype: AbstractFormField
        """
        self.property = prop
        self.locale = locale
        self.level = level
        self.lemma = lemma
        self._widget = widget

    @property
    def value(self):
        """This must be implemented by all subclasses to retrieve the property
        definition as it has been set by the end user via some GUI mechanism.

        :returns: the value of the property in the current field
        :rtype: object
        """
        raise NotImplementedError('Override me')

    @value.setter
    def value(self, value):
        """This must be implemented by all subclasses to set the property
        value via some GUI mechanism (depending on the widget).

        :param value: the new value of the property
        :type value: object
        :rtype: None
        """
        raise NotImplementedError('Override me')

    @QtCore.pyqtSlot(str)
    def update_lemma(self, lemma):
        """Use to automatically update the lemma of the field when a text input
        gets edited by the user via signal-slot mechanism.

        :param lemma: new lemma of the field
        :type lemma: str
        :rtype: None
        """
        self.lemma = lemma


class TextField(AbstractFormField):
    """Textual field to define simple textual properties.
    """

    def __init__(self, prop, level, widget, locale=None, lemma=None):
        super(TextField, self).__init__(prop, level, widget, locale, lemma)

    @property
    def value(self):
        return self._widget.toPlainText()

    @value.setter
    def value(self, value):
        self._widget.setPlainText(value)


class PicklistField(AbstractFormField):
    """Field used to represent picklist properties, where the internal widget
    is a library combo box.
    """

    def __init__(self, prop, level, widget, locale=None, lemma=None):
        super(PicklistField, self).__init__(prop, level, widget, locale,
                                            lemma)

    @property
    def value(self):
        return self._widget.currentText()

    @value.setter
    def value(self, value):
        index = self._widget.model().stringList().index(value)
        self._widget.setCurrentIndex(index)


class FileField(AbstractFormField):
    """Field used to represent resources whose value is the path on the local
    system where such a resource can be found.
    """

    def __init__(self, prop, level, widget, locale=None, lemma=None):
        super(FileField, self).__init__(prop, level, widget, locale, lemma)

    @property
    def value(self):
        return self._widget.value

    @value.setter
    def value(self, value):
        self._widget.value = value


class AbstractEntryForm(QtGui.QWidget):
    """Base class used for entry creation and update forms, providing the
    common part of the constructor, a couple of utility methods used in both
    kinds of forms, a hook method used to fill-in data with already stored
    terminological information and the signal to emit whenever some part of the
    entry form gets filled.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtCore.QWidget
        :rtype: AbstractEntryForm
        """
        super(AbstractEntryForm, self).__init__(parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self._fields = []
        self._terms = {locale: [] for locale in
                       mdl.get_main_model().open_termbase.languages}
        self._language_layouts = {}

    def _append_language_flag(self, locale, child_layout):
        """Appends to the provided child layout a couple of labels in order to
        display the national flag of the language and its name.

        :param child_layout: layout where the new items are to be added
        :type child_layout: QtGui.QBoxLayout
        :param locale: locale of the language being displayed
        :type locale: str
        :rtype: None
        """
        flag = QtGui.QLabel(self)
        flag.setPixmap(
            QtGui.QPixmap(':/flags/{0}.png'.format(locale)).scaledToHeight(
                15))
        label_text = '<strong>{0}</strong>'.format(
            mdl.DEFAULT_LANGUAGES[locale])
        label = LanguageLabel(locale, label_text, self)
        # enables the flag context menu
        flag.contextMenuEvent = label.contextMenuEvent
        # creates a sublayout
        flag_sublayout = QtGui.QHBoxLayout()
        flag_sublayout.addWidget(flag)
        flag_sublayout.addWidget(label)
        flag_sublayout.addStretch()
        child_layout.addLayout(flag_sublayout)

    @QtCore.pyqtSlot()
    def _handle_entry_changed(self):
        """ This slot is called to inform the controller that some input field
        has been filled or that its content has changed.

        :rtype: None
        """
        self.fire_event.emit('entry_changed', {})

    def get_entry_level_property_values(self):
        """Allows the controller to access the information inserted in the
        form by the user for entry-level properties.

        :returns: a dictionary keyed by property IDs containing the values
        specified for entry-level properties
        :rtype: dict
        """
        return {f.property.prop_id: f.value
                for f in self._fields if f.level == 'E'}

    def get_language_level_property_values(self):
        """Allows the controller to access the information inserted in the form
        by the user for language-level properties.

        :returns: a dictionary whose keys are (locale, property-ID) 2-tuples,
        containing the values specified for language-level properties
        :rtype: dict
        """
        return {(locale, f.property.prop_id): f.value
                for locale in mdl.get_main_model().open_termbase.languages
                for f in self._fields if f.level == 'L' and f.locale == locale}

    def get_term_level_property_values(self):
        """ Allows the controller to access the information specified by the
        user for term-level properties.

        :returns: a dictionary whose keys are (locale, lemma, property-ID)
        3-tuples containing the values specified for term-level properties.
        :rtype: dict
        """
        # dictcomp with triple nested for loops, because READABILITY COUNTS...
        return {(locale, lemma, f.property.prop_id): f.value
                for locale in mdl.get_main_model().open_termbase.languages
                for lemma in self.get_terms()[locale]
                for f in self._fields
                if f.level == 'T' and f.locale == locale and f.lemma == lemma}

    def get_terms(self):
        """Allows to access the terms that have been inserted in the form for
        the currently displayed entry. Since more than one term can appear for
        each language, every locale is associated with a list of lemmata.

        :returns: a dictionary keyed by locale IDs containing for each language
        the list of terms that the entry contains.
        :rtype: dict
        """
        return {locale: [f.text() for f in self._terms[locale]]
                for locale in mdl.get_main_model().open_termbase.languages}

    def _fill_field(self, prop, field):
        """Fills a given form field with the information that is currently
        stored in the terminological database in the given property. Particular
        attention must be payed to account for the *type* of the property in
        order to correctly display the information in the GUI and the *level*
        of the property in order to query the right data access layer object.

        :param prop: property whose value must be retrieved and displayed
        :type prop: Property
        :param field: reference to the field to be filled
        :type field: AbstractFormField
        :rtype: None
        """
        raise NotImplementedError('Implement me!')

    def _populate_fields(self, level, child_layout, locale=None, lemma=None):
        """This method is designed to be called several times in the form
        constructor in order to create the parts of the user interface which
        depend on the termbase properties of some level.

        It has the responsibility of extracting the desired set of properties
        from the termbase (model) and create for each and every one of them a
        label with the property name and a suitable input field depending on the
        property type.

        The label and the input field are eventually added to the passed-in
        child layout.

        :param level: level of the properties to be queried
        :type level: str
        :param child_layout: layout where the fields must be added
        :type child_layout: QtGui.QFormLayout
        :param locale: locale of the language (if any) the property refers to
        :type locale: str
        :rtype: None
        """
        for prop in mdl.get_main_model().open_termbase.schema.get_properties(
                level):
            label = QtGui.QLabel(prop.name, self)
            if prop.property_type == 'T':  # text property
                widget = QtGui.QTextEdit(self)
                widget.setMaximumHeight(30)
                widget.textChanged.connect(self._handle_entry_changed)
                field = TextField(prop, level, widget)
            elif prop.property_type == 'I':  # image property
                widget = SelectFileInput(self)
                field = FileField(prop, level, widget)
                widget.path_changed.connect(self._handle_entry_changed)
            else:  # picklist
                widget = QtGui.QComboBox(self)
                model = QtGui.QStringListModel(prop.values)
                widget.setModel(model)
                widget.currentIndexChanged.connect(
                    lambda unused_idx: self._handle_entry_changed())
                field = PicklistField(prop, level, widget)
            if level in ['L', 'T'] and locale:
                field.locale = locale
            if level == 'T' and lemma:
                field.lemma = lemma
            self._fields.append(field)
            # fills-in the widget
            self._fill_field(prop, field)
            # finally appends the widgets to the form layout
            label.setWordWrap(True)
            child_layout.addRow(label, widget)

    @property
    def is_new(self):
        """This property must be overridden by subclasses to help the controller
        determine whether the entry being manipulated in the form is a totally
        new entry or an existing entry in the currently opened termbase.

        :returns: True is the entry is new, False if it already exists
        :rtype: bool
        """
        raise NotImplementedError('Override me!')


class CreateEntryForm(AbstractEntryForm):
    """Widget used to represent the form which is to be displayed whenever the
    user asks to create a new terminological entry. It must contain an
    indication of the languages (with the corresponding flags) that are stored
    in the termbase and just one term input field for each language in order
    to insert the lemma.

    As far as properties are concerned, it must display a set of input fields,
    namely:
    - all entry level properties must have the corresponding field shown once;
    - language level properties must appear once for every language in the
      termbase, under the corresponding flag;
    - term level properties are displayed once for every term under the term
      lemma.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the container widget
        :type parent: QtGui.QWidget
        :rtype: CreateEntryForm
        """
        super(CreateEntryForm, self).__init__(parent)
        # inserts entry-level properties
        entry_property_layout = QtGui.QFormLayout()
        self._populate_fields('E', entry_property_layout)
        self.layout().addLayout(entry_property_layout)
        for locale in mdl.get_main_model().open_termbase.languages:
            # adds flag and language name
            self._language_layouts[locale] = QtGui.QVBoxLayout()
            self._append_language_flag(locale, self._language_layouts[locale])
            # inserts language-level properties
            language_property_layout = QtGui.QFormLayout()
            self._populate_fields('L', language_property_layout, locale)
            self._language_layouts[locale].addLayout(language_property_layout)
            # inserts term-level fields
            term_widget = CustomMenuTermWidget(self)
            term_widget.setLayout(QtGui.QFormLayout(term_widget))
            term_label = QtGui.QLabel('<strong>Term</strong>', self)
            term_input = QtGui.QLineEdit(self)
            self._terms[locale].append(term_input)
            term_widget.layout().addRow(term_label, term_input)
            self._populate_fields('T', term_widget.layout(), locale)
            for field in [f for f in self._fields if
                          f.level == 'T' and f.locale == locale
                          and f.lemma is None]:
                # needed to keep field bound to the term in the input field
                term_input.textChanged.connect(field.update_lemma)
            self._language_layouts[locale].addWidget(term_widget)
            self.layout().addLayout(self._language_layouts[locale])
        self.layout().addStretch()

    def _fill_field(self, prop, field):
        """In entry creation forms nothing has to be done in this step.
        """
        pass

    @property
    def is_new(self):
        """Overridden to correctly implement superclass interface.

        :returns: True since this model is used to create a brand new entry
        :rtype: bool
        """
        return True


class UpdateEntryForm(AbstractEntryForm):
    """This form is used to update an existing entry in the currently opened
    termbase, it shows all properties in editable fields (in a suitable widget
    according to the property type) and initializes their content depending on
    the values stored in the termbase.
    """

    def __init__(self, entry, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtCore.QWidget
        :param entry: terminological Entry that is being edited
        :type entry: Entry
        :rtype: UpdateEntryForm
        """
        super(UpdateEntryForm, self).__init__(parent)
        self.entry = entry
        entry_property_layout = QtGui.QFormLayout()
        self._populate_fields('E', entry_property_layout)
        self.layout().addLayout(entry_property_layout)
        for locale in mdl.get_main_model().open_termbase.languages:
            # adds flag and language name
            self._language_layouts[locale] = QtGui.QVBoxLayout()
            self._append_language_flag(locale, self._language_layouts[locale])
            self._populate_fields('L', self._language_layouts[locale], locale)
            # fields for the terms (possibly more than one)
            for term in self.entry.get_terms(locale):
                term_widget = CustomMenuTermWidget(self)
                term_widget.setLayout(QtGui.QFormLayout(term_widget))
                term_label = QtGui.QLabel('<strong>Term</strong>', self)
                term_input = QtGui.QLineEdit(self)
                term_input.setText(term.lemma)
                self._terms[locale].append(term_input)
                term_widget.layout().addRow(term_label, term_input)
                self._populate_fields('T', term_widget.layout(), locale,
                                      term.lemma)
                for field in [f for f in self._fields if
                              f.level == 'T' and f.locale == locale
                              and f.lemma == term.lemma]:
                    # needed to keep field bound to the term in the input field
                    term_input.textChanged.connect(field.update_lemma)
                self._language_layouts[locale].addWidget(term_widget)
            self.layout().addLayout(self._language_layouts[locale])
        self.layout().addStretch()

    def _fill_field(self, prop, field):
        """Fills the field of the form with the value that is stored in the
        currently opened termbase, getting the value from the data access layer
        and calling the setter on the field.

        :param prop: property that is being accessed
        :type prop: Property
        :param field: field that must be filled
        :type field: AbstractFormField
        :rtype: None
        """
        value = None
        if field.level == 'E':  # entry-level field
            value = self.entry.get_property(prop.prop_id)
        elif field.level == 'L':  # language-level field
            value = self.entry.get_language_property(field.locale,
                                                     prop.prop_id)
        else:  # term-level field
            term = self.entry.get_term(field.locale, field.lemma)
            if term:
                value = term.get_property(prop.prop_id)
        if value:
            field.value = value

    @property
    def is_new(self):
        """Overridden to correctly implement superclass interface.

        :returns: False since this model is used to manipulate existing entries
        :rtype: bool
        """
        return False

    @QtCore.pyqtSlot(str)
    def handle_add_term(self, locale):
        """This slot is activated when the action to add a new term to the
        language with the given locale is triggered. It has the responsibility
        of creating the new input fields and appending them in the correct part
        of the entry update form.

        :param locale: locale of the language where the term must be added
        :type locale: str
        :rtype: None
        """
        term_widget = CustomMenuTermWidget(self)
        term_widget.setLayout(QtGui.QFormLayout(term_widget))
        term_label = QtGui.QLabel('<strong>Term</strong>', self)
        term_input = QtGui.QLineEdit(self)
        term_widget.layout().addRow(term_label, term_input)
        self._terms[locale].append(term_input)
        self._populate_fields('T', term_widget.layout(), locale)
        for field in [f for f in self._fields if
                      f.level == 'T' and f.locale == locale
                      and f.lemma is None]:
            # needed to keep field bound to the term in the input field
            term_input.textChanged.connect(field.update_lemma)
        term_input.setText('')
        self._language_layouts[locale].addWidget(term_widget)

        @QtCore.pyqtSlot(str, str)
        def handle_delete_term(self, locale, lemma):
            pass


class LanguageLabel(QtGui.QLabel):
    """This is basically a library QLabel with just one difference: when the
    context menu is requested, a custom QMenu is provided in order to allow
    users to add new terms for the given language when operating on an entry.
    """

    def __init__(self, locale, text, parent):
        """Constructor method.

        :param locale: ID of the language the label is for
        :type locale: str
        :param text: text to be shown in the label
        :type text: str
        :param parent: reference *to the container form*
        :type parent: AbstractEntryForm
        :rtype: LanguageLabel
        """
        super(LanguageLabel, self).__init__(text, parent)
        self._add_term_action = QtGui.QAction('Add term', self)
        if parent.is_new:  # when the entry is new just one term is allowed
            self._add_term_action.setEnabled(False)
        self._add_term_action.triggered.connect(
            lambda: parent.handle_add_term(locale))

    def contextMenuEvent(self, event):
        """Overridden in order to display a context menu which allows new terms
        to be added to the terminological entry for the given language.

        :param event: this is basically used to determine where to show the menu
        :type event: QtGui.QContextMenuEvent
        :rtype: None
        """
        super(LanguageLabel, self).contextMenuEvent(event)
        context_menu = QtGui.QMenu('Language menu', self)
        context_menu.addAction(self._add_term_action)
        context_menu.show()
        context_menu.move(event.globalPos())


class CustomMenuTermWidget(QtGui.QWidget):
    """This widget behaves almost likely a normal 'plain' QWidget with the
    only notable exception that it provides a custom context menu allowing
    users to operate on the term that is displayed inside it, e.g. removing
    it (visually) from the entry it belongs to. It will be the controller
    responsibility at a later moment to reflect the change in the termbase.
    """

    def __init__(self, locale, lemma, is_vedette, parent):
        """Constructor method.

        :param locale: locale of the term language
        :type locale: str
        :param lemma: lemma of the term
        :type lemma: str
        :param is_vedette: flag indicating whether the term is a vedette
        for the given language or not
        :type is_vedette: bool
        :param parent: reference to the *container form*
        :type parent: QtGui.QWidget
        """
        super(CustomMenuTermWidget, self).__init__(parent)
        self._delete_term_action = QtGui.QAction('Delete term', self)
        if is_vedette:
            self._delete_term_action.setEnabled(False)
        self._delete_term_action.triggered.connect(
            lambda: parent.handle_term_deleted(locale, lemma))

    def contextMenuEvent(self, event):
        """Overridden in order to provide users with a custom context menu.

        :param event: reference to the event being handled, it is needed
        in order to determine the position where the menu will be shown
        :type event: QtGui.QContextMenuEvent
        """
        super(CustomMenuTermWidget, self).contextMenuEvent(event)
        context_menu = QtGui.QMenu('Term menu', self)
        context_menu.addAction(self._delete_term_action)
        context_menu.show()
        context_menu.move(event.globalPos())

