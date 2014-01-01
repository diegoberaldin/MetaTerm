# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entry.forms

This module contains the definition of the forms that are used in order to
create new terminological entries or to modify existing ones.
"""

from PyQt4 import QtCore, QtGui

from src import model as mdl
from src.view.entry import fields


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
        # locale-keyed dictionary of the language widgets
        self._language_widgets = {}
        # locale-keyed dictionary of term widgets (a list for every locale)
        self._term_widgets = {locale: [] for locale in
                              mdl.get_main_model().open_termbase.languages}

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
        return {locale: [w.lemma for w in self._term_widgets[locale] if w.lemma]
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
            if prop.property_type == 'T':  # text property
                field = fields.TextField(prop, level, self, locale, lemma)
            elif prop.property_type == 'I':  # image property
                field = fields.FileField(prop, level, self, locale, lemma)
            else:  # picklist
                field = fields.PicklistField(prop, level, self, locale, lemma)
            self._fields.append(field)
            # signal-slot connection
            field.changed.connect(self._handle_entry_changed)
            # fills-in the widget
            self._fill_field(prop, field)
            # finally appends the widgets to the form layout
            label = QtGui.QLabel(prop.name, self)
            label.setWordWrap(True)
            child_layout.addRow(label, field.widget)

    @property
    def is_new(self):
        """This property must be overridden by subclasses to help the controller
        determine whether the entry being manipulated in the form is a totally
        new entry or an existing entry in the currently opened termbase.

        :returns: True is the entry is new, False if it already exists
        :rtype: bool
        """
        raise NotImplementedError('Override me!')

    @property
    def is_valid(self):
        """Checks whether the content of the form is acceptable.

        :returns: True if the content or the form is acceptable and can be
        saved, False otherwise
        :rtype: bool
        """
        term_dict = self.get_terms()
        # checks that there are no (language, lemma) duplicates within the entry
        for locale in term_dict.keys():
            if any((lemma1 == lemma2 for lemma1 in term_dict[locale] for lemma2
                    in term_dict[locale])):
                return False
        return True


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
            # creates the language widget
            language_widget = CustomMenuLanguageWidget(locale, self)
            self._language_widgets[locale] = language_widget
            # inserts language-level properties
            language_property_layout = QtGui.QFormLayout()
            self._populate_fields('L', language_property_layout, locale)
            language_widget.layout().addLayout(language_property_layout)
            # creates the term widget and inserts term-level fields
            term_widget = CustomMenuTermWidget(locale, '', True, self)
            self._term_widgets[locale].append(term_widget)
            term_label = QtGui.QLabel('<strong>Term</strong>', self)
            term_input = QtGui.QLineEdit(self)
            # needed to record changes in the term fields
            term_input.textEdited.connect(
                lambda unused_text: self._handle_entry_changed())
            # needed to keep consistency
            term_input.textChanged.connect(term_widget.update_lemma)
            term_widget.layout().addRow(term_label, term_input)
            self._populate_fields('T', term_widget.layout(), locale)
            # needed to keep field bound to the term in the input field
            for field in [f for f in self._fields if
                          f.level == 'T' and f.locale == locale
                          and f.lemma is None]:
                term_input.textChanged.connect(field.update_lemma)
            language_widget.add_term_widget(term_widget)
            self.layout().addWidget(language_widget)
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
            # creates the language widget
            language_widget = CustomMenuLanguageWidget(locale, self)
            self._language_widgets[locale] = language_widget
            language_property_layout = QtGui.QFormLayout()
            self._populate_fields('L', language_property_layout, locale)
            language_widget.layout().addLayout(language_property_layout)
            # create term widgets and inserts term-level fields
            for term in self.entry.get_terms(locale):
                term_widget = CustomMenuTermWidget(locale, term.lemma,
                                                   term.vedette, self)
                self._term_widgets[locale].append(term_widget)
                term_label = QtGui.QLabel('<strong>Term</strong>', self)
                term_input = QtGui.QLineEdit(self)
                term_input.setText(term.lemma)
                # needed to record changes in the term fields
                term_input.textEdited.connect(
                    lambda unused_text: self._handle_entry_changed())
                # needed to keep consistency
                term_input.textChanged.connect(term_widget.update_lemma)
                term_widget.layout().addRow(term_label, term_input)
                self._populate_fields('T', term_widget.layout(), locale,
                                      term.lemma)
                # needed to keep fields bound to the term in the input field
                for field in [f for f in self._fields if
                              f.level == 'T' and f.locale == locale
                              and f.lemma == term.lemma]:
                    term_input.textChanged.connect(field.update_lemma)
                language_widget.add_term_widget(term_widget)
            self.layout().addWidget(language_widget)
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
        term_widget = CustomMenuTermWidget(locale, '', False, self)
        term_label = QtGui.QLabel('<strong>Term</strong>', self)
        term_input = QtGui.QLineEdit(self)
        # needed to record changes in the term fields
        term_input.textEdited.connect(
            lambda unused_text: self._handle_entry_changed())
        term_widget.layout().addRow(term_label, term_input)
        # keeps the link between the term widget and the input field
        term_input.textChanged.connect(term_widget.update_lemma)
        self._populate_fields('T', term_widget.layout(), locale)
        # needed to keep field bound to the term in the input field
        for field in [f for f in self._fields if
                      f.level == 'T' and f.locale == locale
                      and f.lemma is None]:
            term_input.textChanged.connect(field.update_lemma)
        term_input.setText('')
        # registers the field internally and displays the widget visually
        self._term_widgets[locale].append(term_widget)
        self._language_widgets[locale].add_term_widget(term_widget)
        # informs the controller that the entry has been changed
        self._handle_entry_changed()

    @QtCore.pyqtSlot(str, str)
    def handle_delete_term(self, locale, lemma):
        """This slot is activated when the user chooses to delete a (non
        vedette) term from the terminological entry. It has the responsibility
        of removing the fields corresponding to the given term visually as well
        as to remove the term from the internal data structure containing the
        reference to the widgets.

        *Note:* no field removal from the self._fields list is actually needed,
        since those fields will automatically be excluded when extracting
        term-level properties with ``get_term_level_property_values`` having no
        correspondence in the ``get_terms`` output.

        :param locale: ID of the language of the term being deleted
        :type locale: str
        :param lemma: lemma of the term being deleted
        :type lemma: str
        :rtype: None
        """
        # extracts the correct term widgets
        term_widget = [w for w in self._term_widgets[locale] if
                       w.lemma == lemma].pop()
        # removes it visually and from the internal fields
        self._language_widgets[locale].remove_term_widget(term_widget)
        self._term_widgets[locale].remove(term_widget)
        # informs the controller that the entry has been changed
        self._handle_entry_changed()


class CustomMenuLanguageWidget(QtGui.QLabel):
    """This is basically a library QLabel with just one difference: when the
    context menu is requested, a custom QMenu is provided in order to allow
    users to add new terms for the given language when operating on an entry.
    """

    def __init__(self, locale, parent):
        """Constructor method.

        :param locale: ID of the language the label is for
        :type locale: str
        :param parent: reference *to the container form*
        :type parent: AbstractEntryForm
        :rtype: LanguageLabel
        """
        super(CustomMenuLanguageWidget, self).__init__(parent)
        self._add_term_action = QtGui.QAction('Add term', self)
        if parent.is_new:  # when the entry is new just one term is allowed
            self._add_term_action.setEnabled(False)
        self._add_term_action.triggered.connect(
            lambda: parent.handle_add_term(locale))
        # initializes the widget layout
        self.setLayout(QtGui.QVBoxLayout(self))
        self._append_language_flag(locale)

    def _append_language_flag(self, locale):
        """Appends a national flag and the name of the language to the language
        widget, by adding a sublayout. It requires that the language widget
        layout be a QBoxLaout subclass, though.

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
        label = QtGui.QLabel(label_text, self)
        # creates a sub-layout
        flag_sub_layout = QtGui.QHBoxLayout()
        flag_sub_layout.addWidget(flag)
        flag_sub_layout.addWidget(label)
        flag_sub_layout.addStretch()
        self.layout().addLayout(flag_sub_layout)

    def contextMenuEvent(self, event):
        """Overridden in order to display a context menu which allows new terms
        to be added to the terminological entry for the given language.

        :param event: this is basically used to determine where to show the menu
        :type event: QtGui.QContextMenuEvent
        :rtype: None
        """
        super(CustomMenuLanguageWidget, self).contextMenuEvent(event)
        context_menu = QtGui.QMenu('Language menu', self)
        context_menu.addAction(self._add_term_action)
        context_menu.show()
        context_menu.move(event.globalPos())

    def add_term_widget(self, widget):
        """Displays a new term widget among the language widget children.

        :param widget: term widget to be added to the layout
        :type widget: CustomMenuTermWidget
        :rtype: None
        """
        self.layout().addWidget(widget)

    def remove_term_widget(self, widget):
        """Removes a term widget from those being displayed as children of the
        language widget layout.

        :param widget: term widget to be removed
        :type widget: CustomMenuTermWidget
        :rtype: None
        """
        self.layout().removeWidget(widget)


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
        self.lemma = lemma
        self._delete_term_action = QtGui.QAction('Delete term', self)
        if is_vedette:
            self._delete_term_action.setEnabled(False)
        self._delete_term_action.triggered.connect(
            lambda: parent.handle_delete_term(locale, self.lemma))
        # initializes the widget layout
        self.setLayout(QtGui.QFormLayout(self))

    def contextMenuEvent(self, event):
        """Overridden in order to provide users with a custom context menu.

        :param event: reference to the event being handled, it is needed
        in order to determine the position where the menu will be shown
        :type event: QtGui.QContextMenuEvent
        """
        # Here we do not delegate to superclass implementation because the
        # context menu of the container widget (i.e. the language widget) must
        # *not* be displayed so no bubbling to parent's event handler is needed
        context_menu = QtGui.QMenu('Term menu', self)
        context_menu.addAction(self._delete_term_action)
        context_menu.show()
        context_menu.move(event.globalPos())

    @QtCore.pyqtSlot(str)
    def update_lemma(self, text):
        """Updates the lemma that is used for this CustomMenuTermWidget
        identification, in order to keep it consistent with the content of
        the term input field.

        :param text: new lemma of the term
        :type text: str
        :rtype: None
        """
        self.lemma = text
