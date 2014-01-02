# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.dataaccess.orm

This package contains the 'low-level' (not so deeply low, though) modules which
the Data Access Layer is built upon, i.e. the configuration of the mapping
between objects and database records, corresponding to the mapping module, and
the access to database files on disk as well as the base class used for mapping
in the sql module.
"""

from src.model.dataaccess.orm.mapping import (
    Entry, EntryLanguageAssociation,
    EntryPropertyAssociation, EntryLanguagePropertyAssociation, Term,
    TermPropertyAssociation, Language, Property, PickListValue)
from src.model.dataaccess.orm.sql import (
    write_to_disk, DB_DIR, initialize_tb_folder, get_termbase_names)
