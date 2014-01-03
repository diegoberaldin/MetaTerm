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
.. currentmodule:: src.model.itemmodels

This package contains all the ``QtCore.QAbstractItemModel`` subclasses that are
used to those (tree and list) models which are to be connected to standard
library view in order to reflect part of the information stored in the termbase.
"""

from src.model.itemmodels.termbasedefinition import (TermbaseDefinitionModel,
                                                     PropertyNode)
from src.model.itemmodels.entry import EntryModel
