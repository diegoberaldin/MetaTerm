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
.. currentmodule:: src.model

This package contains the modules which the application model is made up of.
These include the ``sql`` module where the basic configuration of SQLAlchemy is
 performed, ``mapping`` where all transfer object are defined and ``dataaccess``
which contains the object-oriented data access layer of the application.
"""

from src.model.dataaccess import Termbase
from src.model.dataaccess.orm import initialize_tb_folder, get_termbase_names
from src.model.itemmodels import (TermbaseDefinitionModel,
                                  PropertyNode, EntryModel)
from src.model.main import get_main_model
