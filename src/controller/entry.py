# -*- coding: utf-8 -*-
#
# MetaTerm - A terminology management application written in Python
# Copyright (C) 2013 Diego Beraldin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further information, contact the authors at <diego.beraldin@gmail.com>.

"""
.. currentmodule:: src.controller.entry

This module contains the controller that governs entry creation, update and
deletion and manages entry visualization in the graphical user interface.
"""

from PyQt4 import QtGui

from src.controller.abstract import AbstractController
from src import model as mdl


class EntryController(AbstractController):
    """Controller that is responsible for entry visualization and manipulation.
    It has two reference models: the 'global' main model with its open termbase
    and a specific instance of ``model.itemmodels.entry.EntryModel`` that is
    manipulated via a set of accessor methods. The governed view corresponds to
    the main widget of the application with its entry list and entry display,
    but the events to which it reacts *can be originated everywhere in the UI*
    even in the main window and outside the entry display/manipulation area.
    """

    def __init__(self, entry_model, entry_view):
        """Constructor method.

        :param entry_model: reference to the entry model representing the entry
        set of the currently opened termbase
        :type entry_model: EntryModel
        :param entry_view: reference to the application main widget
        :type entry_view: EntryWidget
        :rtype: EntryController
        """
        super(EntryController, self).__init__()
        self._model = entry_model
        self._view = entry_view
        # sets the language of the entry model
        self._model.language = self._view.entry_list.current_language

    def _handle_language_changed(self):
        """This handler is activated when the GUI language selector state is
         changed, in this case the language of the entry model must be changed

        :rtype: None
        """
        self._model.language = self._view.entry_list.current_language

    def _handle_new_entry(self):
        """This handler is activated when the user starts the creation of a new
        terminological entry. It has the responsibility of clearing the content
        of the entry display in the view and showing the entry creation form.

        :rtype: None
        """
        self._view.entry_display.display_create_entry_form()

    def _handle_save_entry(self):
        """This handler is activated when the user requests to save an entry
        which may either be a newly created one or an existing one after an
        update. The controller must then determine whether to insert a new entry
        or update an existing one, extract the information provided in the
        form, make it persistent in the local termbase and put the UI in a
        consistent state (displaying the updated entry).

        :rtype: None
        """
        form = self._view.entry_display.content
        if not form.is_valid:
            message = QtGui.QMessageBox()
            message.setIcon(QtGui.QMessageBox.Critical)
            message.setText('Invalid entry')
            message.setInformativeText('Check that all the mandatory fields '
                                       'are filled-in and that there are not '
                                       'terms with the same lemma within the '
                                       'same language in this entry.')
            message.exec()
            # don't do anything of the rest
            return
        if form.is_new:
            # creates the new entry
            entry = mdl.get_main_model().open_termbase.create_entry()
            # inserts all terms
            for (locale, lemmata) in form.get_terms().items():
                assert len(lemmata) == 1
                lemma = lemmata.pop()
                entry.add_term(lemma, locale, True)
        else:  # manipulating an existing entry
            entry = form.entry
        for (property_id,
             value) in form.get_entry_level_property_values().items():
            # inserts entry-level properties
            entry.set_property(property_id, value)
        for ((language_id, property_id),
             value) in form.get_language_level_property_values().items():
            # insert language-level properties
            entry.set_language_property(language_id, property_id, value)
        for ((locale, lemma, property_id),
             value) in form.get_term_level_property_values().items():
            # inserts term properties
            term = entry.get_term(locale, lemma)
            if not term:  # term has been added during entry edit
                entry.add_term(lemma, locale, False)
                term = entry.get_term(locale, lemma)  # now it is there!
            term.set_property(property_id, value)
            # updates the entry model
        if form.is_new:  # insertion
            self._model.add_entry(entry)
        else:  # an existing entry is being edited
            # checks for deleted terms
            terms_to_delete = [
                term for term in [t for locale in
                                  mdl.get_main_model().open_termbase.languages
                                  for t in entry.get_terms(locale)]  # all terms
                if (term.locale, term.lemma) not in [(locale, lemma) for
                                                     locale, lemmata_list
                                                     in form.get_terms().items()
                                                     for lemma in lemmata_list]]
            # assuring no vedette term is **ever** deleted
            assert all(not term.vedette for term in terms_to_delete)
            # actually deletes the term
            for term in terms_to_delete:
                entry.delete_term(term)
                # the dataChanged() signal must be emitted
            self._model.update_entry(entry)
            # updates the UI
        self._view.entry_display.display_entry(entry)
        self._view.entry_list.sort_entries()

    def _handle_entry_index_changed(self, index):
        """This handler is activated when the user selects a new entry in the
        GUI list. In this case the controller must update the content of the
        entry display in order to show the information about the selected entry.

        :param index: index pointing to the new selected entry
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        selected_entry = self._model.get_entry(index)
        self._view.entry_display.display_entry(selected_entry)

    def _handle_edit_entry(self):
        """This handler is activated when the user requests to edit the entry
        that is currently being shown in the GUI entry display. It has the
        responsibility of extracting the entry and displaying the update entry
        form in order to start the editing operation.

        :rtype: None
        """
        entry = self._view.entry_display.current_entry
        self._view.entry_display.display_update_entry_form(entry)

    def _handle_delete_entry(self):
        """This handler is activated when the user asks to delete the entry that
        is currently being displayed in the GUI. The controller must then
        extract the entry, delete it permanently from the currently opened
        termbase, remove it from the entry model and reset the GUI.

        :rtype: None
        """
        entry = self._view.entry_display.current_entry
        mdl.get_main_model().open_termbase.delete_entry(entry)
        self._model.delete_entry(entry)
        self._view.entry_list.sort_entries()
        self._view.entry_display.display_welcome_screen()

    def _handle_edit_canceled(self):
        """When the user cancels an entry creation or update operation, the
        UI must be put in a consistent state by deleting the current form and
        showing either the entry information or the welcome screen.

        :rtype: None
        """
        entry = self._view.entry_display.current_entry
        if entry:
            self._view.entry_display.display_entry(entry)
        else:
            self._view.entry_display.display_welcome_screen()
