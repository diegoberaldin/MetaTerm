# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.dataaccess

Object-oriented data access layer of the application which is used as an abstraction level built on top of the data
persistence level in order not to deal with mapping and (detatched) transfer objects all the time.
"""

from contextlib import contextmanager
import os
import uuid

import sqlalchemy.orm
from sqlalchemy.exc import SQLAlchemyError

from src.model import sql
from src.model import mapping


class TermBase(object):
    """Representation of a terminological database.
    """

    def __init__(self, name):
        """Creates a new termbase with the given name.

        :param name: name of the termbase
        """
        self.name = name
        session = sqlalchemy.orm.sessionmaker(self._get_engine())
        self._session = sqlalchemy.orm.scoped_session(session)
        # writes the termbase on disk (if needed)
        sql.write_to_disk(self._get_termbase_file_name(), self._get_engine())

    def _get_termbase_file_name(self):
        """Returns the name of the file where the database is stored.

        :returns: name of the local file where the termbase is stored
        :rtype: str
        """
        return os.path.join(sql.DB_DIR, self.name)

    def _get_connection_string(self):
        """Returns the connection string to be used to interact with the local database associated to this termbase.

        :returns: string to be used to connect with the DB (through an engine)
        :rtype: str
        """
        return 'sqlite:///{0}.sqlite'.format(self._get_termbase_file_name())

    def _get_engine(self):
        """Returns an engine used to create sessions and to write DB metadata to disk when the termbase is made
        persistent.

        :returns: an engine object to interact with the termbase
        :rtype: object
        """
        return sqlalchemy.create_engine(self._get_connection_string())

    @contextmanager
    def get_session(self):
        """Returns a transactional session to be used in with statements to manipulate the content of the invocation
        termbase.

        :returns: session to be used in with blocks
        :rtype: object
        """
        session = self._session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
        finally:
            session.close()

    @property
    def schema(self):
        """
        Returns a handle to modify the termbase information schema.

        :returns: a Schema object to manipulate the termbase schema
        :rtype: Schema
        """
        return Schema(self)

    def create_entry(self):
        """Creates a new entry of the termbase and returns an entry instance.

        :returns: the newly created entry
        :rtype: Entry
        """
        entry_id = uuid.uuid4()
        # adds a new entry into the termbase
        with self.get_session() as session:
            entry = mapping.Entry(entry_id=entry_id)
            session.add(entry)
        return Entry(entry_id, self)

    def add_language(self, locale):
        """Adds the language with the given locale to the termbase languages.

        :param locale: the locale of the language
        :type locale: str
        :rtype: None
        """
        with self.get_session() as session:
            language = mapping.Language(locale=locale)
            session.add(language)


class Schema(object):
    """Instances of this class are used to manipulate the information schema associated to the given termbase.
    """

    def __init__(self, termbase):
        """Constructor method.

        :param termbase: termbase instance whose schema is being modified
        :type termbase: TermBase
        """
        self._tb = termbase

    def add_property(self, name, level, prop_type='T', values=()):
        """Adds a new property to the termbase.

        :param name: name of the property
        :type name: str
        :param level: level of the property (entry, language or term)
        :type level: str
        :param prop_type: type of the property (picklist, text or image)
        :type prop_type: str
        :param values: list of possible picklist values
        :type values: tuple
        :rtype: None
        """
        # it is impossible to create empty picklists
        assert prop_type != 'P' or values
        with self._tb.get_session() as session:
            prop_id = uuid.uuid4()
            prop = mapping.Property(name=name, prop_id=prop_id, level=level, prop_type=prop_type)
            session.add(prop)
            # adds the possible values for picklist properties
            for picklist_value in values:
                value = mapping.PickListValue(prop_id=prop_id, value=picklist_value)
                session.add(value)

    def delete_property(self, prop_id):
        """Deletes of a property from the termbase schema.

        :param prop_id: ID of the property to be deleted
        :type prop_id: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            session.query(mapping.Property).filter(mapping.Property.prop_id == prop_id).delete()


class Entry(object):
    """High level representation of a terminological entry of the termbase.
    """

    def __init__(self, entry_id, termbase):
        """Constructor method.

        :param entry_id: ID of the entry
        :type entry_id: str
        :param termbase: termbase which the entry belongs to
        :type termbase: TermBase
        """
        self._tb = termbase
        self.id = entry_id

    def create_term(self, lemma, locale, vedette):
        """Adds a new term to the terminological entry.

        :param lemma: string representation of the term
        :type lemma: str
        :param locale: language ID associated with the term
        :type locale: str
        :param vedette: flag indicating whether the term is a vedette or not
        :type vedette: bool
        :returns: the newly created term instance
        :rtype: Term
        """
        term_id = uuid.uuid4()
        with self._tb.get_session() as session:
            term = mapping.Term(term_id=self.id, lemma=lemma, lang_id=locale, vedette=vedette, entry_id=self.id)
            session.add(term)
        return Term(term_id, lemma, locale, vedette, self._tb)

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
                mapping.EntryPropertyAssociation.entry_id == self.id).scalar()

    def set_property(self, prop_id, value):
        """Changes the value of a given property for the invocation entry.

        :param prop_id: ID of the property involved
        :type prop_id: str
        :param value: the new value of the property
        :type value: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            prop = session.query(mapping.EntryPropertyAssociation).filter(
                mapping.EntryPropertyAssociation.prop_id == prop_id,
                mapping.EntryPropertyAssociation.entry_id == self.id).first()
            prop.value = value

    def get_language_property(self, lang_id, prop_id):
        """Gets the value of a language level property for the invocation terminological entry.

        :param lang_id: ID of the language involved
        :type lang_id: str
        :param prop_id: ID of the property involved
        :type prop_id: str
        :returns: the value of the property for the given entry/language pair
        :rtype: str
        """
        with self._tb.get_session() as session:
            ela_id = session.query(mapping.EntryLanguageAssociation.ela_id).filter(
                mapping.EntryLanguageAssociation.entry_id == self.id,
                mapping.EntryLanguageAssociation.lang_id == lang_id).scalar()
            return session.query(mapping.EntryLanguagePropertyAssociation.value).filter(
                mapping.EntryLanguagePropertyAssociation.ela_id == ela_id,
                mapping.EntryLanguagePropertyAssociation.prop_id == prop_id).scalar()

    def set_language_property(self, lang_id, prop_id, value):
        """Changes the value of a language level property for the invocation terminological entry.

        :param lang_id: ID of the language involved
        :type lang_id: str
        :param prop_id: ID of the property involved
        :type prop_id: str
        :param value: new value of the property for the entry/language pair
        :type value: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            ela_id = session.query(mapping.EntryLanguageAssociation.ela_id).filter(
                mapping.EntryLanguageAssociation.entry_id == self.id,
                mapping.EntryLanguageAssociation.lang_id == lang_id).scalar()
            prop = session.query(mapping.EntryLanguagePropertyAssociation).filter(
                mapping.EntryLanguagePropertyAssociation.ela_id == ela_id,
                mapping.EntryLanguagePropertyAssociation.prop_id == prop_id).one()
            prop.value = value


class Term(object):
    """High level representation of a term within a terminological entry in a termbase.
    """

    def __init__(self, term_id, lemma, locale, vedette, termbase):
        """Constructor method.

        :param term_id: ID of the term
        :type term_id: int
        :param lemma: string representation of the term
        :type lemma: str
        :param locale: language ID to associate the term with a language
        :type locale: str
        :param vedette: flag indicating whether the term is a vedette or not for the language
        :type vedette: bool
        :param termbase: reference to the containing termbase
        :type termbase: TermBase
        """
        self.id = term_id
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
            return session.query(mapping.TermPropertyAssociation.value).filter(
                mapping.TermPropertyAssociation.term_id == self.id,
                mapping.TermPropertyAssociation.prop_id == prop_id).scalar()

    def set_property(self, prop_id, value):
        """Changes the current value of a given property.

        :param prop_id: ID of the property involved
        :param value: new value of the property
        :rtype: None
        """
        with self._tb.get_session() as session:
            prop = session.query(mapping.TermPropertyAssociation).filter(
                mapping.TermPropertyAssociation.term_id == self.id,
                mapping.TermPropertyAssociation.prop_id == prop_id).first()
            prop.value = value
