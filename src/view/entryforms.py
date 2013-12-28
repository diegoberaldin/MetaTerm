# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entryforms

This module contains the definition of the forms that are used in order to
create new terminological entries or to modify existing ones.
"""

import os

from PyQt4 import QtCore, QtGui

from src import model as mdl


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
        self.setLayout(QtGui.QFormLayout(self))
        self._fields = []
        self._terms = {locale: [] for locale in
                       mdl.get_main_model().open_termbase.languages}

    def _append_language_flag(self, locale):
        """Appends a read-only row to the form displaying the national flag of
        the language with the given locale as well as its name.

        :param locale: locale of the language being displayed
        :type locale: str
        :rtype: None
        """
        flag = QtGui.QLabel(self)
        flag.setPixmap(
            QtGui.QPixmap(':/flags/{0}.png'.format(locale)).scaledToHeight(
                15))
        label = QtGui.QLabel(
            '<strong>{0}</strong>'.format(mdl.DEFAULT_LANGUAGES[locale]),
            self)
        self.layout().addRow(flag, label)

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
                for f in self._fields if f.level == 'T' and f.locale == locale}

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

    def _populate_fields(self, level, locale=None, lemma=None):
        """This method is designed to be called several times in the form
        constructor in order to create the parts of the user interface which
        depend on the termbase properties of some level.

        It has the responsibility of extracting the desired set of properties
        from the termbase (model) and create for each and every one of them a
        label with the property name and a suitable input field depending on the
        property type.

        :param level: level of the properties to be queried
        :type level: str
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
            self.layout().addRow(label, widget)


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
        self._populate_fields('E')
        for locale in mdl.get_main_model().open_termbase.languages:
            # adds flag and language name
            self._append_language_flag(locale)
            self._populate_fields('L', locale)
            # field for the term
            term_label = QtGui.QLabel('<strong>Term</strong>', self)
            term_input = QtGui.QLineEdit(self)
            self._terms[locale].append(term_input)
            self.layout().addRow(term_label, term_input)
            self._populate_fields('T', locale)

    def _fill_field(self, prop, field):
        """In entry creation forms nothing has to be done in this step.
        """
        pass


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


class TextField(AbstractFormField):
    """Textual field to define simple textual properties.
    """

    def __init__(self, prop, level, widget, locale=None, lemma=None):
        super(TextField, self).__init__(prop, level, widget, locale, lemma)

    @property
    def value(self):
        return self._widget.toPlainText()


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


class FileField(AbstractFormField):
    """Field used to represent resources whose value is the path on the local
    system where such a resource can be found.
    """

    def __init__(self, prop, level, widget, locale=None, lemma=None):
        super(FileField, self).__init__(prop, level, widget, locale, lemma)

    @property
    def value(self):
        return self._widget.value
