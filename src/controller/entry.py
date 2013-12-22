# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.controller.entry

"""

from src.controller.abstract import AbstractController


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

    def __del__(self):  # TODO: I'm not sure this is the right thing to do
        self._view.entry_display.display_welcome_screen()
