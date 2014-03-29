# -*- coding: utf-8 -*-
#
# MetaTerm - A terminology management application written in Python
# Copyright (C) 2014 Diego Beraldin
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
.. currentmodule:: src.model.dataaccess.schema

This module contains the classes used to represent and manipulate the structure
of the target terminological database, i.e. the definition model, which can be
queried and is accessible via the 'schema' property of each termbase instance.
"""

import uuid

from src.model.dataaccess import orm


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
            prop = orm.Property(name=name, prop_id=prop_id, level=level,
                                prop_type=prop_type)
            session.add(prop)
            # adds the possible values for picklist properties
            for picklist_value in values:
                value = orm.PickListValue(prop_id=prop_id,
                                          value=picklist_value)
                session.add(value)

    def delete_property(self, prop_id):
        """Deletes of a property from the termbase schema.

        :param prop_id: ID of the property to be deleted
        :type prop_id: str
        :rtype: None
        """
        with self._tb.get_session() as session:
            session.query(orm.Property).filter(
                orm.Property.prop_id == prop_id).delete()

    def get_properties(self, level):
        """Returns a list of all the properties that a given termbase schema
        owns at the entry, language or term level.

        :param level: string indicating the requested level
        :type level: str
        :return: a list of Property object containing those elements that match
        the required criteria
        :rtype: list
        """
        assert level in ['E', 'L', 'T']
        with self._tb.get_session() as session:
            return [Property(p.prop_id, p.name, self._tb) for p in
                    session.query(orm.Property).filter(
                        orm.Property.level == level)]


class Property(object):
    """High level representation of a property, which is characterized only by
    its ID and a textual name.
    """

    def __init__(self, prop_id, name, termbase):
        """Constructor method.

        :param prop_id: ID of the new property
        :type prop_id: str
        :param name: name of the the new property
        :type name: str
        :param termbase: reference to the container termbase
        :type termbase: Termbase
        :rtype: Property
        """
        self.prop_id = prop_id
        self.name = name
        self._tb = termbase

    @property
    def property_type(self):
        """Returns a string literal containing an indication on the property
        type (i.e. whether a property is textual, an image or a picklist).

        :return: an indication of the type in ``['T', 'I', 'P']``
        :rtype: str
        """
        with self._tb.get_session() as session:
            return session.query(orm.Property.prop_type).filter(
                orm.Property.prop_id == self.prop_id).scalar()

    @property
    def values(self):
        """Returns a list of all the possible values that a given property
        can have according to the termbase schema. Non-picklist properties
        will always return an empty string since the set of legal values for
        them is empty in the termbase schema.

        :return: a list (possibly empty) of all legal values
        :rtype: list
        """
        with self._tb.get_session() as session:
            return [v[0] for v in
                    session.query(orm.PickListValue.value).filter(
                        orm.PickListValue.prop_id == self.prop_id)]

    def __eq__(self, other):
        if hasattr(other, 'prop_id'):
            return self.prop_id == other.prop_id
        return False
