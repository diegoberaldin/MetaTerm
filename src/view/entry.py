# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entry

This module contains the definition of the classes that are used to display
and manipulate entries in the application main window.
"""

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
        selector = LanguageSelector(self)
        # puts everything together
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(selector)
        self.layout().addWidget(self._view)
        # signal-slot connection
        selector.fire_event.connect(self.fire_event)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value
        self._view.setModel(self._model)


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
            self._handle_index_changed)

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

    @QtCore.pyqtSlot(int)
    def _handle_index_changed(self, unused_index):
        """Determines the locale of the currently selected index in the
        language combobox and has the language selector to emit the right
        signal (with the current locale passed as a parameter)

        :rtype: None
        """
        language_name = self._language_combo.currentText()
        if language_name:
            inverted_languages = {value: key for key, value in
                                  mdl.DEFAULT_LANGUAGES.items()}
            self.fire_event.emit('language_changed',
                                 {'locale': inverted_languages[language_name]})


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
        self._content = None
        # shows greeting
        self.display_welcome_screen()
        # signal-slot connection
        mdl.get_main_model().termbase_closed.connect(
            self.display_welcome_screen)

    def _display_content(self, content):
        if self._content:
            self.layout().removeWidget(self._content)
            self._content.deleteLater()
        self._content = content
        self.layout().addWidget(self._content)

    def display_create_entry_form(self):
        form = CreateEntryForm(self)
        form.fire_event.connect(self.fire_event)
        self._display_content(form)

    @QtCore.pyqtSlot()
    def display_welcome_screen(self):
        self._display_content(WelcomeScreen(self))


class WelcomeScreen(QtGui.QWidget):
    """This class is used to present a welcome screen in the ``EntryDisplay``
    each time the application is started and a termbase is closed.
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
        self._terms = {}
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
            self._terms[locale] = QtGui.QLineEdit(self)
            self.layout().addRow(term_label, self._terms[locale])
            self._populate_fields('T', locale)

    def _populate_fields(self, level, locale=None):
        for prop in mdl.get_main_model().open_termbase.schema.get_properties(
                level):
            label = QtGui.QLabel(prop.name, self)
            property_type = prop.property_type
            if property_type == 'T':
                widget = QtGui.QTextEdit(self)
                widget.setMaximumHeight(30)
                widget.textChanged.connect(self._handle_entry_changed)
            elif property_type == 'I':
                widget = QtGui.QLabel('da cambiare', self)
            else:  # picklist
                widget = QtGui.QComboBox(self)
                model = QtGui.QStringListModel(prop.values)
                widget.setModel(model)
                widget.currentIndexChanged.connect(
                    lambda unused_idx: self._handle_entry_changed())
            field = FormField(prop, locale, widget)
            self._fields.append(field)
            self.layout().addRow(label, widget)

    @QtCore.pyqtSlot()
    def _handle_entry_changed(self):
        self.fire_event.emit('entry_changed', {})


class FormField(object):
    def __init__(self, prop, locale, widget):
        self.property = prop
        self.locale = locale
        self._widget = widget
