# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.dataaccess.termbase

This is the main module of the data access layer, since it contains the
definition of the ``Termbase`` class which interacts directly with the SQL and
mapping modules to create those sessions used to retrieve, update and delete
data on the underlying terminological database. An instance of the containing
termbase is therefore used by all other classes in this package to access the
data persistence level of the system.
"""

from contextlib import contextmanager
import os
import uuid
import logging

import sqlalchemy.orm
from sqlalchemy.exc import SQLAlchemyError

from src.model import sql
from src.model import mapping
from src.model.dataaccess.entry import Entry
from src.model.dataaccess.schema import Schema


# a logger for this module
_LOG = logging.getLogger('src.model.dataaccess')


class Termbase(object):
    """Representation of a terminological database.
    """

    def __init__(self, name):
        """Creates a new termbase with the given name.

        :param name: name of the termbase
        :rtype: Termbase
        """
        self.name = name
        session = sqlalchemy.orm.sessionmaker(self._get_engine())
        self._session = sqlalchemy.orm.scoped_session(session)
        # writes the termbase on disk (if needed)
        sql.write_to_disk(self.get_termbase_file_name(), self._get_engine())

    def get_termbase_file_name(self):
        """Returns the name of the file where the database is stored.

        :returns: name of the local file where the termbase is stored
        :rtype: str
        """
        return os.path.join(sql.DB_DIR, '{0}.sqlite'.format(self.name))

    def _get_connection_string(self):
        """Returns the connection string to be used to interact with the local
        database associated to this termbase.

        :returns: string to be used to connect with the DB (through an engine)
        :rtype: str
        """
        return 'sqlite:///{0}'.format(self.get_termbase_file_name())

    def _get_engine(self):
        """Returns an engine used to create sessions and to write DB metadata to
        disk when the termbase is made persistent.

        :returns: an engine object to interact with the termbase
        :rtype: object
        """
        return sqlalchemy.create_engine(self._get_connection_string())

    @contextmanager
    def get_session(self):
        """Returns a transactional session to be used in with statements to
        manipulate the content of the invocation termbase.

        :returns: session to be used in with blocks
        :rtype: object
        """
        session = self._session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as exc:
            _LOG.exception(exc)
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
        entry_id = str(uuid.uuid4())
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

    @property
    def languages(self):
        """Returns an iterable with the locales stored in the current termbase.

        :returns: a list of all the termbase locales
        :rtype: list
        """
        with self.get_session() as session:
            return [l[0] for l in session.query(mapping.Language.locale)]

    @property
    def entry_number(self):
        """Returns the total number of entries that exist in the termbase.

        :returns: number of entries of the termbase
        :rtype: int
        """
        with self.get_session() as session:
            return session.query(mapping.Entry).count()

    @property
    def size(self):
        """Queries the underlying file system for the total size that the
        currently open termbase requires.

        :returns: a string representing the total size of the termbase
        :rtype: int
        """
        size = os.path.getsize(self.get_termbase_file_name())
        return self.format_size(size)

    @staticmethod
    def format_size(space):
        """Returns an appropriate string with human-readable information about
        an amount of space on disk.

        :param space: original size
        :type space: int
        :returns: a string with a human-readable size
        :rtype: str
        """
        if space < 1024:
            return '{0} bytes'.format(space)
        elif space < 1048576:
            return '{0:.2f} KB'.format(float(space) / 1024)
        elif space < 1073741824:
            return '{0:.2f} MB'.format(float(space) / 1048576)
        else:
            return '{0:.2f} GB'.format(float(space) / 1073741824)

    @property
    def entries(self):
        with self.get_session() as session:
            return [Entry(e.entry_id, self) for e in
                    session.query(mapping.Entry)]
