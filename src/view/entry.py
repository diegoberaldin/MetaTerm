# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entry

This module contains the definition of the classes that are used to display
and manipulate entries in the application main window.
"""

import os

from PyQt4 import QtCore, QtGui

from src import model as mdl


class EntryWidget(QtGui.QSplitter):
    """Central widget that is displayed inside the application main window,
    whose purpose is to display a list of the entries of the current termbase
    (if any) and a central part which acts as a form to create/edit entries
    or a display to show terminological information about them.
    """
    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted when an event needs to be notified to the controller."""

    def __init__(self, parent):
        """Constructor method

            :param parent: reference to the main window
            :type parent: QtCore.QWidget
            :rtype: EntryWidget
            """
        super(EntryWidget, self).__init__(parent)
        self._entry_model = None
        self.entry_list = EntryList(self)
        self.entry_display = EntryDisplay(self)
        # puts everything together
        self.addWidget(self.entry_list)
        self.addWidget(self.entry_display)
        self.setSizes([200, 400])
        # signal-slot connection
        self.entry_list.fire_event.connect(self.fire_event)
        self.entry_display.fire_event.connect(self.fire_event)

    @property
    def entry_model(self):
        """Returns a reference to the entry model that is currently used in
        this widget to display the entry list.

        :return: reference to the current entry model
        """
        return self._entry_model

    @entry_model.setter
    def entry_model(self, value):
        """Allows the controller to inject a new reference to the model when
        it is needed.

        :param value: reference to the new model
        :type value: QtCore.QAbstractItemModel
        :rtype: None
        """
        self.entry_list.model = value


class EntryList(QtGui.QWidget):
    """List of all the entries that are stored in the current termbase.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtCore.QWidget
        :rtype: EntryList
        """
        super(EntryList, self).__init__(parent)
        self._model = None
        self._view = QtGui.QListView(self)
        self._selector = LanguageSelector(self)
        # puts everything together
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self._selector)
        self.layout().addWidget(self._view)
        # signal-slot connection
        self._selector.fire_event.connect(self.fire_event)
        self._view.clicked.connect(
            lambda index: self.fire_event.emit('entry_index_changed',
                                               {'index': index}))

    @property
    def model(self):
        """Returns a reference to the entry model which the view is bound to.

        :returns: a reference to the current entry model
        """
        return self._model

    @model.setter
    def model(self, value):
        """Allows to change the model that the entry list is bound to, namely
        altering the model that is connected to the internal list view.

        :param value: reference to the new model
        :type value: EntryModel
        :rtype: None
        """
        self._model = value
        self._view.setModel(self._model)

    @property
    def current_language(self):
        """Returns the locale of the language that is currently selected in the
        entry list ``LanguageSelector`` internal instance.

        :returns: the locale of the currently selected language
        :rtype: str
        """
        return self._selector.current_language


class LanguageSelector(QtGui.QWidget):
    """This widget corresponds to the upper part of the entry list and it
    basically displays a combobox in order for the user to change the main
    language in which the termbase is displayed.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent of the widget
        :type parent: QtCore.QWidget
        :rtype: LanguageSelector
        """
        super(LanguageSelector, self).__init__(parent)
        self.setLayout(QtGui.QHBoxLayout(self))
        self.layout().addWidget(QtGui.QLabel('Language', self))
        self._language_combo = QtGui.QComboBox(self)
        self.layout().addWidget(self._language_combo)
        # signal-slot connection
        mdl.get_main_model().termbase_opened.connect(
            self._regenerate_language_list)
        mdl.get_main_model().termbase_closed.connect(
            self._regenerate_language_list)
        self._language_combo.currentIndexChanged.connect(
            lambda: self.fire_event.emit('language_changed', {}))

    @QtCore.pyqtSlot()
    def _regenerate_language_list(self):
        """Updates the list of the current languages depending on the languages
        that are available in the currently opened termbase. If the slot is
        activated upon a termbase closure, the list of languages is emptied.

        :rtype: None
        """
        if mdl.get_main_model().open_termbase:  # termbase opened
            locale_list = [mdl.DEFAULT_LANGUAGES[locale] for locale in
                           mdl.get_main_model().open_termbase.languages]
        else:  # termbase closed
            locale_list = []
        model = QtGui.QStringListModel(locale_list)
        self._language_combo.setModel(model)

    @property
    def current_language(self):
        """Determines the locale of the currently selected index in the
        language combobox returns it as a string.

        :returns: the locale of the currently selected language or None
        :rtype: str
        """
        language_name = self._language_combo.currentText()
        if language_name:
            inverted_languages = {value: key for key, value in
                                  mdl.DEFAULT_LANGUAGES.items()}
            return inverted_languages[language_name]


class EntryDisplay(QtGui.QWidget):
    """This class is used to model the main part of the application GUI, where
    terminological entries are displayed, edited and created.
    """

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the container widget (the central widget)
        :type parent: QtGui.QWidget
        :rtype: EntryDisplay
        """
        super(EntryDisplay, self).__init__(parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.content = None
        # shows greeting
        self.display_welcome_screen()
        # signal-slot connection
        mdl.get_main_model().termbase_closed.connect(
            self.display_welcome_screen)

    def _display_content(self, content):
        """Eases the change of content that is displayed inside the entry view
        by discarding the previous internal widget (and removing it completely)
        while inserting the new one in the widget layout.

        :param content: reference to the new inner widget
        :type content: QtGui.QWidget
        :rtype: None
        """
        if self.content:
            self.layout().removeWidget(self.content)
            self.content.deleteLater()
        self.content = content
        self.layout().addWidget(self.content)

    def display_create_entry_form(self):
        """Displays the form for the creation of a new terminological entry in
        the entry view of the main widget.

        :rtype: None
        """
        form = CreateEntryForm(self)
        # this is needed for event propagation
        form.fire_event.connect(self.fire_event)
        self._display_content(form)

    @QtCore.pyqtSlot()
    def display_welcome_screen(self):
        """Displays the initial welcome screen inside the entry display.

        :rtype: None
        """
        self._display_content(WelcomeScreen(self))

    def display_entry(self, entry):
        self._display_content(EntryScreen(entry, self))


class EntryScreen(QtGui.QWidget):
    def __init__(self, entry, parent):
        super(EntryScreen, self).__init__(parent)
        self.setLayout(QtGui.QFormLayout(self))
        self._entry = entry
        entry_id_label = QtGui.QLabel(
            '<small>Entry ID: {0}</small>'.format(self._entry.entry_id))
        self.layout().addWidget(entry_id_label)
        schema = mdl.get_main_model().open_termbase.schema
        for prop in schema.get_properties('E'):
            # shows entry-level properties
            prop_label = QtGui.QLabel('<strong>{0}:</strong>'.format(prop.name),
                                      self)
            value_label = QtGui.QLabel(
                self._entry.get_property(prop.prop_id), self)
            self.layout().addRow(prop_label, value_label)
        for locale in mdl.get_main_model().open_termbase.languages:
            # adds flag and language name
            flag = QtGui.QLabel(self)
            flag.setPixmap(
                QtGui.QPixmap(':/flags/{0}.png'.format(locale)).scaledToHeight(
                    15))
            label = QtGui.QLabel(
                '<strong>{0}</strong>'.format(mdl.DEFAULT_LANGUAGES[locale]),
                self)
            self.layout().addRow(flag, label)
            for prop in schema.get_properties('L'):
                # shows language-level properties
                prop_label = QtGui.QLabel(
                    '<strong>{0}:</strong>'.format(prop.name),
                    self)
                value_label = QtGui.QLabel(
                    self._entry.get_language_property(locale, prop.prop_id),
                    self)
                self.layout().addRow(prop_label, value_label)
            for term in self._entry.get_terms(locale):
                if term.vedette:
                    # if the term is the vedette, it must be printed in bold
                    term_label = QtGui.QLabel(
                        '<strong>{0}</strong>'.format(term.lemma), self)
                else:
                    term_label = QtGui.QLabel(term.lemma, self)
                self.layout().addWidget(term_label)
                for prop in schema.get_properties('T'):
                    # adds term-level properties
                    prop_label = QtGui.QLabel(
                        '<strong>{0}:</strong>'.format(prop.name),
                        self)
                    value_label = QtGui.QLabel(term.get_property(prop.prop_id),
                                               self)
                    self.layout().addRow(prop_label, value_label)


class WelcomeScreen(QtGui.QWidget):
    """This class is used to present a welcome screen in the ``EntryDisplay``
    each time the application is started and a termbase is closed. The content
    of such a widget is statically determined at compile time.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the container widget
        :type parent: QtGui.QWidget
        :rtype: CreateEntryForm
        """
        super(WelcomeScreen, self).__init__(parent)
        text = ('<h1>Welcome to MetaTerm!</h1>'
                '<strong>MetaTerm</strong> is an application that helps you '
                'creating and maintaining terminological databases .<br /> '
                'If you want to create a new termbase go to <code>Termbase &gt;'
                'New...</code> in order to start the creation wizard.<br />'
                'To open an existing termbase go to <code>Termbase &gt; '
                'Open...</code> and choose one of the available items.')
        label = QtGui.QLabel(text, self)
        label.setWordWrap(True)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(label)

        # def paintEvent(self, event):
        #     """Overridden to have the stylesheet applied.
        #
        #     :param event: reference to the paint event (unused)
        #     :rtype: None
        #     """
        #     option = QtGui.QStyleOption()
        #     option.init(self)
        #     painter = QtGui.QPainter(self)
        #     style = self.style()
        #     style.drawPrimitive(QtGui.QStyle.PE_Widget, option, painter, self)


class CreateEntryForm(QtGui.QWidget):
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

    fire_event = QtCore.pyqtSignal(str, dict)
    """Signal emitted to notify the controller about events.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the container widget
        :type parent: QtGui.QWidget
        :rtype: CreateEntryForm
        """
        super(CreateEntryForm, self).__init__(parent)
        self.setLayout(QtGui.QFormLayout(self))
        self._fields = []
        self._terms = {locale: [] for locale in
                       mdl.get_main_model().open_termbase.languages}
        self._populate_fields('E')
        for locale in mdl.get_main_model().open_termbase.languages:
            # adds flag and language name
            flag = QtGui.QLabel(self)
            flag.setPixmap(
                QtGui.QPixmap(':/flags/{0}.png'.format(locale)).scaledToHeight(
                    15))
            label = QtGui.QLabel(
                '<strong>{0}</strong>'.format(mdl.DEFAULT_LANGUAGES[locale]),
                self)
            self.layout().addRow(flag, label)
            self._populate_fields('L', locale)
            term_label = QtGui.QLabel('<strong>Term</strong>', self)
            term_input = QtGui.QLineEdit(self)
            self._terms[locale].append(term_input)
            self.layout().addRow(term_label, term_input)
            self._populate_fields('T', locale)

    def _populate_fields(self, level, locale=None):
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
            if level in ['L', 'T']:
                field.locale = locale
                # keeps the _fields property up-to-date with the changes
            self._fields.append(field)
            # finally appends the widgets to the form layout
            self.layout().addRow(label, widget)

    @QtCore.pyqtSlot()
    def _handle_entry_changed(self):
        """ This slot is called to inform the controller that some input field
        has been filled or that its content has changed.

        :rtype: None
        """
        self.fire_event.emit('entry_changed', {})

    # @property unsupported in QtCore.QWidget subclasses :(
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
                                                      os.path.expanduser(
                                                          '~'))
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
