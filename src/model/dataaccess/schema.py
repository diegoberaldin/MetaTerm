# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.dataaccess.schema

This module contains the classes used to represent and manipulate the structure
of the target terminological database, i.e. the definition model, which can be
queried and is accessible via the 'schema' property of each termbase instance.
"""

import uuid

from src.model import mapping


class Schema(object):
    """Instances of this class are used to manipulate the information schema
    associated to the given termbase.
    """

    def __init__(self, termbase):
        """Constructor method.

        :param termbase: termbase instance whose schema is being modified
        :type termbase: Termbase
        :rtype: Schema
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
        :returns: the newly created property
        :rtype: None
        """
        # it is impossible to create empty picklists
        assert prop_type != 'P' or values
        with self._tb.get_session() as session:
            prop_id = str(uuid.uuid4())
            prop = mapping.Property(name=name, prop_id=prop_id, level=level,
                                    prop_type=prop_type)
            session.add(prop)
            # adds the possible values for picklist properties
            for picklist_value in values:
                value = mapping.PickListValue(prop_id=prop_id,
                                              value=picklist_value)
                session.add(value)

    def delete_property(self, prop_id):
        """Deletes of a property from the termbase schema.

        :param prop_id: ID of the property to be deleted
        :type prop_id: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            session.query(mapping.Property).filter(
                mapping.Property.prop_id == prop_id).delete()


class Property(object):
    """High level representation of a property, which is characterized only by
    its ID and a textual name.
    """

    def __init__(self, prop_id, name):
        """Constructor method.

        :param prop_id: ID of the new property
        :type prop_id: str
        :param name: name of the the new property
        :type name: str
        :rtype: Property
        """
        self.prop_id = prop_id
        self.name = name
