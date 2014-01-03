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
.. currentmodule:: src.model.dataaccess.entry

This module contains the classes that are used to represent entries within a
terminological database and allow to set/get entry level properties and add
terms to an entry reflecting those changes in the data persistence level.
"""

import uuid

import sqlalchemy
import sqlalchemy.orm

from src.model.dataaccess import orm
from src.model.dataaccess.term import Term


class Entry(object):
    """High level representation of a terminological entry of the termbase,
    which is characterized by its ID only.
    """

    def __init__(self, entry_id, termbase):
        """Constructor method.

        :param entry_id: ID of the entry
        :type entry_id: str
        :param termbase: termbase which the entry belongs to
        :type termbase: Termbase
        :rtype : Entry
        """
        self._tb = termbase
        self.entry_id = entry_id

    def get_vedette(self, locale):
        """Retrieves the lemma of the vedette term for the language with the ID
        equal to the given locale that is contained in the terminological entry.

        :param locale: ID of the language of which the vedette term is needed
        :type locale: str
        :returns: the lemma of the vedette term of the invocation entry having
        the given locale as its language ID
        :rtype: str
        """
        if not locale:
            return
        with self._tb.get_session() as session:
            return session.query(orm.Term.lemma).filter(
                orm.Term.entry_id == self.entry_id,
                orm.Term.lang_id == locale,
                orm.Term.vedette == True).scalar()

    def add_term(self, lemma, locale, vedette):
        """Adds a new term to the terminological entry.

        :param lemma: string representation of the term
        :type lemma: str
        :param locale: language ID associated with the term
        :type locale: str
        :param vedette: flag indicating whether the term is a vedette or not
        :type vedette: bool
        :returns: the newly created term instance
        :rtype: None
        """
        term_id = str(uuid.uuid4())
        with self._tb.get_session() as session:
            term = orm.Term(term_id=term_id, lemma=lemma,
                            lang_id=locale, vedette=vedette,
                            entry_id=self.entry_id)
            session.add(term)

    def delete_term(self, term):
        """Deletes a term from the given terminological entry.

        :param term: term to remove from the entry
        :type term: Term
        :return:
        """
        with self._tb.get_session() as session:
            # deletes term properties
            session.query(orm.TermPropertyAssociation).filter(
                orm.TermPropertyAssociation.term_id == term.term_id).delete()
            # actual term deletion
            session.query(orm.Term).filter(
                orm.Term.term_id == term.term_id).delete()

    def get_property(self, prop_id):
        """Gets the value of a given property for the invocation entry.

        :param prop_id: ID of the property involved
        :type prop_id: str
        :return: the value of the given property for this entry
        :rtype: str
        """
        with self._tb.get_session() as session:
            return session.query(orm.EntryPropertyAssociation.value).filter(
                orm.EntryPropertyAssociation.prop_id == prop_id,
                orm.EntryPropertyAssociation.entry_id == self.entry_id
            ).scalar()

    def set_property(self, prop_id, value):
        """Changes the value of a given property for the invocation entry.

        :param prop_id: ID of the property involved
        :type prop_id: str
        :param value: the new value of the property
        :type value: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            try:
                prop = session.query(orm.EntryPropertyAssociation).filter(
                    orm.EntryPropertyAssociation.prop_id == prop_id,
                    orm.EntryPropertyAssociation.entry_id == self.entry_id
                ).one()
                if value:
                    prop.value = value
                else:
                    session.delete(prop)
            except sqlalchemy.orm.exc.NoResultFound:
                # the property had not been set previously
                if prop:
                    prop = orm.EntryPropertyAssociation(entry_id=self.entry_id,
                                                        prop_id=prop_id,
                                                        value=value)
                    session.add(prop)

    def get_language_property(self, lang_id, prop_id):
        """Gets the value of a language level property for the invocation
        terminological entry.

        :param lang_id: ID of the language involved
        :type lang_id: str
        :param prop_id: ID of the property involved
        :type prop_id: str
        :returns: the value of the property for the given entry/language pair
        :rtype: str
        """
        with self._tb.get_session() as session:
            ela_id = session.query(
                orm.EntryLanguageAssociation.ela_id).filter(
                orm.EntryLanguageAssociation.entry_id == self.entry_id,
                orm.EntryLanguageAssociation.lang_id == lang_id).scalar()
            return session.query(
                orm.EntryLanguagePropertyAssociation.value).filter(
                orm.EntryLanguagePropertyAssociation.ela_id == ela_id,
                orm.EntryLanguagePropertyAssociation.prop_id == prop_id
            ).scalar()

    def set_language_property(self, lang_id, prop_id, value):
        """Changes the value of a language level property for the invocation
        terminological entry.

        :param lang_id: ID of the language involved
        :type lang_id: str
        :param prop_id: ID of the property involved
        :type prop_id: str
        :param value: new value of the property for the entry/language pair
        :type value: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            ela_id = session.query(
                orm.EntryLanguageAssociation.ela_id).filter(
                orm.EntryLanguageAssociation.entry_id == self.entry_id,
                orm.EntryLanguageAssociation.lang_id == lang_id).scalar()
            if not ela_id:  # the association had not been created previously
                ela_id = str(uuid.uuid4())
                ela = orm.EntryLanguageAssociation(ela_id=ela_id,
                                                   entry_id=self.entry_id,
                                                   lang_id=lang_id)
                session.add(ela)
            try:
                prop = session.query(
                    orm.EntryLanguagePropertyAssociation).filter(
                    orm.EntryLanguagePropertyAssociation.ela_id == ela_id,
                    orm.EntryLanguagePropertyAssociation.prop_id == prop_id
                ).one()
                if value:
                    prop.value = value
                else:
                    session.delete(prop)
            except sqlalchemy.orm.exc.NoResultFound:
                # the property had not been set previously
                if value:
                    prop = orm.EntryLanguagePropertyAssociation(ela_id=ela_id,
                                                                prop_id=prop_id,
                                                                value=value)
                    session.add(prop)

    def get_term(self, locale, lemma):
        """Returns a Term (data access) object corresponding to the term that is
        contained in the invocation entry having the given locale and the given
        lemma.

        :param locale: ID of the language of the desired term
        :param lemma: lemma of the desired term
        :returns: a (data access) Term object to manipulate the term if some
        term exists corresponding to the given criteria, None otherwise
        :rtype: Term
        """
        with self._tb.get_session() as session:
            try:
                term = session.query(orm.Term).filter(
                    orm.Term.entry_id == self.entry_id,
                    orm.Term.lang_id == locale,
                    orm.Term.lemma == lemma).one()
                return Term(term.term_id, term.lemma, term.lang_id,
                            term.vedette,
                            self._tb)
            except sqlalchemy.orm.exc.NoResultFound:
                return None

    def get_terms(self, locale):
        """Returns the list of terms that are stored in the termbase under the
        given entry and for the language with the given locale.

        :param locale: ID of the language whose terms must be retrieved
        :type locale: str
        :returns: list of Term objects corresponding to the entry terms
        :rtype: list
        """
        with self._tb.get_session() as session:
            return [Term(t.term_id, t.lemma, t.lang_id, t.vedette, self._tb) for
                    t in session.query(orm.Term).filter(
                    orm.Term.entry_id == self.entry_id,
                    orm.Term.lang_id == locale)]
