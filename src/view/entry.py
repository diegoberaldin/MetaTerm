# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entry

This module contains the definition of the classes that are used to display
and manipulate entries in the application main window.
"""

from PyQt4 import QtCore, QtGui
from src import model as mdl


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
                           mdl.get_main_model().open_termbase.get_languages()]
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

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the containing (main) widget
        :type parent: QtGui.QWidget
        :rtype: EntryDisplay
        """
        super(EntryDisplay, self).__init__(parent)
