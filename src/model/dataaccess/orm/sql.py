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
.. currentmodule:: src.model.sql

This module contains the types and constants that are needed in order to handle
the data persistence layer, i.e. a constant representing the location where
termbases are stored and a mechanism to initialize it on the target system, the
function used to make termbases persistent once they are created for the first
time and, most notably, the base class which is extended by all transfer objects
and by means of which the ORM is made possible.
"""

import os

import sqlalchemy.ext.declarative

DB_DIR = os.path.join(os.path.expanduser('~'), '.metaterm')
"Location where the termbases will be stored."

Mappable = sqlalchemy.ext.declarative.declarative_base()
"Base for all ORM mapping classes."


def initialize_tb_folder():
    """Creates the folder where all termbases will be stored.

    :rtype: None
    """
    if not os.path.exists(DB_DIR):
        os.mkdir(DB_DIR)


def get_termbase_names():
    """Returns the list of all termbases available on the system.

    :returns: a list of absolute file names corresponding to termbases
    :rtype: list
    """
    return [name for name in os.listdir(DB_DIR) if name.endswith('.sqlite')]


def write_to_disk(tb_name, engine):
    """Creates an empty termbase in a local file.

    :param tb_name: name of the termbase to be saved
    :type tb_name: str
    :param engine: SQLAlchemy engine to use
    :type engine: object
    :rtype: None
    """
    if not os.path.exists(tb_name):
        Mappable.metadata.create_all(engine)
