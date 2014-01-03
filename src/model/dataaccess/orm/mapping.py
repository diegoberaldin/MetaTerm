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
.. currentmodule:: src.model.dataaccess.orm.mapping

This module contains all transfer object definitions used to perform the
object-relational mapping with SQLAlchemy. This is the basis for the data access
layer too.
"""

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Boolean, Enum

from src.model import constants
from src.model.dataaccess.orm import sql


class Entry(sql.Mappable):
    """Representation of a terminological entry.
    """
    # name of the corresponding table
    __tablename__ = 'Entries'
    # field mapping
    entry_id = Column(String, primary_key=True)


class EntryPropertyAssociation(sql.Mappable):
    """Association class between termbase entries and properties.
    """
    # name of the corresponding table
    __tablename__ = 'EntryPropertyAssoc'
    # field mapping
    entry_id = Column('entry_id', String,
                      ForeignKey('Entries.entry_id', ondelete='CASCADE'),
                      primary_key=True)
    prop_id = Column('prop_id', String,
                     ForeignKey('Properties.prop_id', ondelete='CASCADE'),
                     primary_key=True)
    value = Column('value', String, nullable=False)


class Language(sql.Mappable):
    """Representation of a termbase language.
    """
    # name of the corresponding table
    __tablename__ = 'Languages'
    # field mapping
    locale = Column(String, primary_key=True)


class EntryLanguageAssociation(sql.Mappable):
    """Association class between termbase entries and languages.
    """
    # name of the corresponding table
    __tablename__ = 'EntryLanguageAssoc'
    # field mapping
    ela_id = Column(String, primary_key=True)
    entry_id = Column(String,
                      ForeignKey('Entries.entry_id', ondelete='CASCADE'))
    lang_id = Column(String, ForeignKey('Languages.locale', ondelete='CASCADE'))
    # other constraints
    UniqueConstraint('entry_id', 'lang_id')


class EntryLanguagePropertyAssociation(sql.Mappable):
    """Association class between the EntryLanguageAssociation and Properties,
     used to capture language level properties.
    """
    # name of the corresponding table
    __tablename__ = 'EntryLanguageAssocPropertyAssoc'
    # field mapping
    ela_id = Column(String,
                    ForeignKey('EntryLanguageAssoc.ela_id', ondelete='CASCADE'),
                    primary_key=True)
    prop_id = Column(String,
                     ForeignKey('Properties.prop_id', ondelete='CASCADE'),
                     primary_key=True)
    value = Column(String, nullable=False)


class Property(sql.Mappable):
    """Representation of a property in the termbase structure, which may refer
    to entries, languages or single terms according to their level. Properties
    can be picklists, textual or images.
    """
    # name of the corresponding table
    __tablename__ = 'Properties'
    # field mapping
    name = Column(String)
    prop_id = Column(String, primary_key=True)
    level = Column(Enum(*constants.PROP_LEVELS))
    prop_type = Column(Enum(*constants.PROP_TYPES))
    # other constraints
    UniqueConstraint('name', 'level', 'prop_type')


class PickListValue(sql.Mappable):
    """Representation of the value of a picklist property.
    """
    # name of the corresponding table
    __tablename__ = 'PickListValues'
    # field mapping
    prop_id = Column(String,
                     ForeignKey('Properties.prop_id', ondelete='CASCADE'),
                     primary_key=True)
    value = Column(String, primary_key=True)


class Term(sql.Mappable):
    """Representation of a single term within a terminological entry.
    """
    # name of the corresponding table
    __tablename__ = 'Terms'
    # field mapping
    term_id = Column(String, primary_key=True)
    lemma = Column(String, nullable=False)
    lang_id = Column(String, ForeignKey('Languages.locale', ondelete='CASCADE'),
                     nullable=False, )
    vedette = Column(Boolean, nullable=False)
    entry_id = Column(String,
                      ForeignKey('Entries.entry_id', ondelete='CASCADE'),
                      nullable=False)
    # other constraints
    UniqueConstraint('entry_id', 'lang_id', 'lemma')


class TermPropertyAssociation(sql.Mappable):
    """Association class between terms and properties.
    """
    # name of the corresponding table
    __tablename__ = 'TermPropertyAssoc'
    # field mapping
    term_id = Column(String, ForeignKey('Terms.term_id', ondelete='CASCADE'),
                     primary_key=True)
    prop_id = Column(String,
                     ForeignKey('Properties.prop_id', ondelete='CASCADE'),
                     primary_key=True)
    value = Column(String, nullable=False)
