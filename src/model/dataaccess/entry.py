# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.dataaccess.entry

This module contains the classes that are used to represent entries within a
terminological database and allow to set/get entry level properties and add
terms to an entry reflecting those changes in the data persistence level.
"""

import uuid

import sqlalchemy
import sqlalchemy.orm

from src.model import mapping
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
        if not locale:
            return
        with self._tb.get_session() as session:
            return session.query(mapping.Term.lemma).filter(
                mapping.Term.entry_id == self.entry_id,
                mapping.Term.lang_id == locale,
                mapping.Term.vedette == True).scalar()

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
            term = mapping.Term(term_id=term_id, lemma=lemma,
                                lang_id=locale, vedette=vedette,
                                entry_id=self.entry_id)
            session.add(term)

    def get_property(self, prop_id):
        """Gets the value of a given property for the invocation entry.

        :param prop_id: ID of the property involved
        :type prop_id: str
        :return: the value of the given property for this entry
        :rtype: str
        """
        with self._tb.get_session() as session:
            return session.query(mapping.EntryPropertyAssociation.value).filter(
                mapping.EntryPropertyAssociation.prop_id == prop_id,
                mapping.EntryPropertyAssociation.entry_id == self.entry_id
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
                prop = session.query(mapping.EntryPropertyAssociation).filter(
                    mapping.EntryPropertyAssociation.prop_id == prop_id,
                    mapping.EntryPropertyAssociation.entry_id == self.entry_id
                ).one()
                prop.value = value
            except sqlalchemy.orm.exc.NoResultFound:
                # the property had not been set previously
                prop = mapping.EntryPropertyAssociation(entry_id=self.entry_id,
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
                mapping.EntryLanguageAssociation.ela_id).filter(
                mapping.EntryLanguageAssociation.entry_id == self.entry_id,
                mapping.EntryLanguageAssociation.lang_id == lang_id).scalar()
            return session.query(
                mapping.EntryLanguagePropertyAssociation.value).filter(
                mapping.EntryLanguagePropertyAssociation.ela_id == ela_id,
                mapping.EntryLanguagePropertyAssociation.prop_id == prop_id
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
                mapping.EntryLanguageAssociation.ela_id).filter(
                mapping.EntryLanguageAssociation.entry_id == self.entry_id,
                mapping.EntryLanguageAssociation.lang_id == lang_id).scalar()
            if not ela_id:  # the association had not been created previously
                ela_id = str(uuid.uuid4())
                ela = mapping.EntryLanguageAssociation(ela_id=ela_id,
                                                       entry_id=self.entry_id,
                                                       lang_id=lang_id)
                session.add(ela)
            try:
                prop = session.query(
                    mapping.EntryLanguagePropertyAssociation).filter(
                    mapping.EntryLanguagePropertyAssociation.ela_id == ela_id,
                    mapping.EntryLanguagePropertyAssociation.prop_id == prop_id
                ).one()
                prop.value = value
            except sqlalchemy.orm.exc.NoResultFound:
                # the property had not been set previously
                prop = mapping.EntryLanguagePropertyAssociation(ela_id=ela_id,
                                                                prop_id=prop_id,
                                                                value=value)
                session.add(prop)

    def get_term(self, locale, lemma):
        """Returns a Term (dataaccess) object corresponding to the term that is
        contained in the invocation entry having the given locale and the given
        lemma.

        :param locale: ID of the language of the desired term
        :param lemma: lemma of the desired term
        :returns: a (dataaccess) Term object to manipulate the term if some
        term exists corresponding to the given criteria, None otherwise
        :rtype: Term
        """
        with self._tb.get_session() as session:
            try:
                term = session.query(mapping.Term).filter(
                    mapping.Term.lang_id == locale,
                    mapping.Term.lemma == lemma).one()
                return Term(term.term_id, term.lemma, term.lang_id,
                            term.vedette,
                            self._tb)
            except sqlalchemy.orm.exc.NoResultFound:
                return None

    def get_terms(self, locale):
        with self._tb.get_session() as session:
            return [Term(t.term_id, t.lemma, t.lang_id, t.vedette, self._tb) for
                    t in session.query(mapping.Term).filter(
                    mapping.Term.entry_id == self.entry_id,
                    mapping.Term.lang_id == locale)]
