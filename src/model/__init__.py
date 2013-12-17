# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model

This package contains the modules which the application model is made up of.
These include the ``sql`` module where the basic configuration of SQLAlchemy is
 performed, ``mapping`` where all transfer object are defined and ``dataaccess``
which contains the object-oriented data access layer of the application.
"""

from src.model.dataaccess import TermBase
from src.model.sql import initialize_tb_folder, get_termbase_names
from src.model.constants import DEFAULT_LANGUAGES
from src.model.termbasedefinitionmodel import (TermbaseDefinitionModel,
                                               PropertyNode)