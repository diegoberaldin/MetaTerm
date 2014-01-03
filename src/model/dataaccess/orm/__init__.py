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
