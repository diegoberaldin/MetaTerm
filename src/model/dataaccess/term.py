# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.dataaccess.term

This module contains the classes used to represent terms inside a termbase.
"""

import sqlalchemy
import sqlalchemy.orm

from src.model import mapping as orm


class Term(object):
    """High level representation of a term within a terminological entry.
    """

    def __init__(self, term_id, lemma, locale, vedette, termbase):
        """Constructor method.

        :param term_id: ID of the term
        :type term_id: str
        :param lemma: string representation of the term
        :type lemma: str
        :param locale: language ID to associate the term with a language
        :type locale: str
        :param vedette: flag indicating whether the term is a vedette or not
        :type vedette: bool
        :param termbase: reference to the containing termbase
        :type termbase: Termbase
        :rtype: Term
        """
        self.term_id = term_id
        self.lemma = lemma
        self.locale = locale
        self.vedette = vedette
        self._tb = termbase

    def get_property(self, prop_id):
        """Returns the value of a given property.

        :param prop_id: ID of the property involved
        :type prop_id: str
        :returns: a string representing the property value
        :rtype: str
        """
        with self._tb.get_session() as session:
            return session.query(orm.TermPropertyAssociation.value).filter(
                orm.TermPropertyAssociation.term_id == self.term_id,
                orm.TermPropertyAssociation.prop_id == prop_id).scalar()

    def set_property(self, prop_id, value):
        """Changes the current value of a given property.

        :param prop_id: ID of the property involved
        :param value: new value of the property
        :rtype: None
        """
        with self._tb.get_session() as session:
            try:
                prop = session.query(orm.TermPropertyAssociation).filter(
                    orm.TermPropertyAssociation.term_id == self.term_id,
                    orm.TermPropertyAssociation.prop_id == prop_id).one()
                prop.value = value
            except sqlalchemy.orm.exc.NoResultFound:
                # the property had not been set previously
                prop = orm.TermPropertyAssociation(term_id=self.term_id,
                                                   prop_id=prop_id,
                                                   value=value)
                session.add(prop)
