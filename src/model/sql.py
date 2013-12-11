# -*- coding: utf-8 -*-
#
# src/model/sql.py
#
# This module contains the types and constants that are needed in order to handle the data persistence layer, notably
# the TermBase class after which all terminological databases are modeled.

import os

import sqlalchemy.ext.declarative

# location where the termbases will be stored
DB_DIR = os.path.join(os.path.expanduser('~'), '.metaterm')

# base for all ORM mapping classes
Mappable = sqlalchemy.ext.declarative.declarative_base()


def initialize_tb_folder():
    """Creates the folder where all termbases will be stored.
    """
    if not os.path.exists(DB_DIR):
        os.mkdir(DB_DIR)


def write_to_disk(tb_name, engine):
    """Creates an empty termbase in a local file.
    :param tb_name: name of the termbase to be saved
    :param engine: SQLAlchemy engine to use
    """
    if not os.path.exists(tb_name):
        Mappable.metadata.create_all(engine)
