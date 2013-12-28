# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entry

This module contains the definition of the classes that are used to display
and manipulate entries in the application main window.
"""

from PyQt4 import QtCore, QtGui

from src import model as mdl
from src.view.entryforms import CreateEntryForm


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
        """Displays the given entry in a suitable widget in the main area of
        the central widget of the application.

        :param entry: reference to the entry to be displayed
        :type entry: Entry
        :rtype: None
        """
        self._display_content(EntryScreen(entry, self))


class EntryScreen(QtGui.QWidget):
    """Widget that is shown in the central part of the ``EntryDisplay`` to fully
    show a terminological entry without allowing any modification to it.
    """

    def __init__(self, entry, parent):
        """Constructor method.

        :param entry: entry to be displayed
        :type entry: Entry
        :param parent: reference to the parent widget
        :type parent: QtGui.QWidget
        :rtype: EntryScreen
        """
        super(EntryScreen, self).__init__(parent)
        self.setLayout(QtGui.QFormLayout(self))
        self._entry = entry
        entry_id_label = QtGui.QLabel(
            '<small>Entry ID: {0}</small>'.format(self._entry.entry_id))
        self.layout().addWidget(entry_id_label)
        schema = mdl.get_main_model().open_termbase.schema
        for prop in schema.get_properties('E'):
            # shows entry-level properties
            self._show_property(prop.name,
                                self._entry.get_property(prop.prop_id))
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
                value = self._entry.get_language_property(locale, prop.prop_id)
                self._show_property(prop.name, value)
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
                    self._show_property(prop.name,
                                        term.get_property(prop.prop_id))

    def _show_property(self, name, value):
        """Displays a given row in the entry screen, containing the name of the
        property on the left side and the corresponding value on the right side.

        :param name: name of the property to be displayed
        :type name: str
        :param value: value of the property to be displayed
        :type value: str
        :rtype: None
        """
        if value:
            prop_label = QtGui.QLabel('<strong>{0}:</strong>'.format(name), self)
            value_label = QtGui.QLabel(value, self)
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
