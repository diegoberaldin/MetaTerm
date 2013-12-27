# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.controller.entry

"""

from src.controller.abstract import AbstractController
from src import model as mdl


class EntryController(AbstractController):
    def __init__(self, entry_model, entry_view):
        super(EntryController, self).__init__()
        self._model = entry_model
        self._view = entry_view
        # signal-slot connections
        self._view.fire_event.connect(self.handle_event)

    def _handle_language_changed(self, locale):
        self._model.language = locale

    def _handle_new_entry(self):
        self._view.entry_display.display_create_entry_form()

    def _handle_save_entry(self):
        form = self._view.entry_display.content
        # creates the new entry
        new_entry = mdl.get_main_model().open_termbase.create_entry()
        for (property_id,
             value) in form.get_entry_level_property_values().items():
            # inserts entry-level properties
            new_entry.set_property(property_id, value)
        for ((language_id, property_id),
             value) in form.get_language_level_property_values().items():
            # insert language-level properties
            new_entry.set_language_property(language_id, property_id, value)
        for (locale, lemmata) in form.get_terms().items():
            # inserts all terms
            assert len(lemmata) == 1
            lemma = lemmata.pop()
            new_entry.add_term(lemma, locale, True)
        for ((locale, lemma, property_id),
             value) in form.get_term_level_property_values().items():
            # inserts term properties
            term = new_entry.get_term(locale, lemma)
            term.set_property(property_id, value)
        self._view.entry_display.display_welcome_screen()



