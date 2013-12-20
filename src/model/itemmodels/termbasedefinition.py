# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.model.itemmodels.termbasedefinition

This model contains the ``QtCore.QAbstractItemModel`` subclass that is used
to represent the termbase definition model during termbase configuration. The
resulting structure is suitable to be queried by the views being compliant with
the ``QAbstractItemModel`` API.
"""
# it should be queried by the controller too when creating the termbase

from PyQt4 import QtCore


class PropertyNode(object):
    def __init__(self, name='', prop_type=None, parent=None, values=()):
        """Constructor method.

        :param name: label of the node
        :type name: str
        :param prop_type: type of the property in ``['T', 'I', 'P']``
        :type prop_type: str
        :param parent: parent of the node
        :type parent: PropertyNode
        :param values: set of possible values for a picklist
        :type values: tuple
        :rtype: PropertyNode
        """
        if prop_type == 'P':
            assert values
        else:
            assert not values
        self.name = name
        self.type = prop_type
        self.values = values
        self.parent = parent
        if parent:
            parent.children.append(self)
        self.children = []


class TermbaseDefinitionModel(QtCore.QAbstractItemModel):
    def __init__(self):
        """Constructor method.

        :rtype: TermbaseDefinitionModel
        """
        super(TermbaseDefinitionModel, self).__init__()
        self._root = PropertyNode()
        self.initialize_levels()

    def initialize_levels(self):
        """Initializes the first three levels of the tree structure (which are
        the only ones allowed to have children on their own besides the root).

        :rtype: None
        """
        root_index = self.createIndex(0, 0, self._root)
        self.beginInsertRows(root_index, 0, 2)
        entry_level = PropertyNode('Entry level', parent=self._root)
        language_level = PropertyNode('Language level', parent=self._root)
        term_level = PropertyNode('Term level', parent=self._root)
        self.endInsertRows()

    def insert_node(self, level, node):
        """Inserts a new property node in the termbase definition model tree,
        at the level specified by the ``level`` parameter.

        :param level: level where the new property node must be inserted, which
        must be a single character string in ``['E', 'L', 'T']``
        :type level: str
        :param node: the new property node to be inserted
        :type node: PropertyNode
        :rtype: None
        """
        assert level in ['E', 'L', 'T']
        if level == 'E':
            parent = self._root.children[0]
        elif level == 'L':
            parent = self._root.children[1]
        else:
            parent = self._root.children[2]
        child_num = len(parent.children)
        parent_index = self.createIndex(0, 0, parent)
        self.layoutAboutToBeChanged.emit()
        self.beginInsertRows(parent_index, child_num, child_num)
        node.parent = parent
        parent.children.append(node)
        self.endInsertRows()
        self.layoutChanged.emit()

    def delete_node(self, node):
        """Deletes a node from the tree structure of the termbase definition
        model, notifying all connected views about the changes occurring.

        :param node: the node to be removed from the tree
        :type node: PropertyNode
        :rtype: None
        """
        parent = node.parent
        parent_index = self.createIndex(0, 0, parent)
        row = parent.children.index(node)
        self.beginRemoveRows(parent_index, row, row)
        parent.children.remove(node)
        node.parent = None  # these nodes have no children (luckily)
        self.endRemoveRows()

    def alter_node(self, old_node, new_node):
        """Replaces the given old node with another (new) node in the termbase
        definition model tree to allow changes in property definition, i.e.
        converting the type of a property or altering the set of possible values
        that a picklist property can accept.

        :param old_node: old node which must be replaced
        :type old_node: PropertyNode
        :param new_node: new node to be inserted in the tree
        :type new_node: PropertyNode
        :rtype: None
        """
        parent = old_node.parent
        parent_index = self.createIndex(0, 0, parent)
        row = parent.children.index(old_node)
        self.beginRemoveRows(parent_index, row, row)
        parent.children.remove(old_node)
        old_node.parent = None
        self.endRemoveRows()
        child_count = len(parent.children)
        self.beginInsertRows(parent_index, child_count, child_count)
        parent.children.append(new_node)
        new_node.parent = parent  # these nodes have no children (luckily)
        self.endInsertRows()

    def get_property_number(self):
        """Returns the total number of properties that have been created in the
        termbase definition model, no matter the level they belong to.

        :return: the number of properties that have been defined so fare
        :rtype: int
        """
        return sum([len(self._root.children[i].children) for i in range(3)])

    def get_properties(self):
        """Returns a list of the properties that have been configured in the
        invocation termbase definition model. These are represented as
        dictionaries with the ``name``, ``level``, ``prop_type`` and ``values``
        keys designed to be compatible with the ``create_property`` method
        of schema objects.

        :returns: a list of dictionaries used to define the properties that
        were found at the given level
        :rtype: list
        """
        levels = ['E', 'L', 'T']
        # list of dictionaries generated via double list comprehension iterating
        # over a generator, is it readable, though?
        return [{'name': node.name, 'level': level, 'prop_type': node.type,
                 'values': node.values} for level, parent_node in
                zip(levels, self._root.children) for
                node in parent_node.children]

    def flags(self, index):
        """Indicates that the items of this model are selectable and enabled
        by default but they cannot be edited directly.

        :param index: the index to be queried
        :type index: QtCore.QModelIndex
        :return: a combination of the index flags
        :rtype: int
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Allows views connected to this model to display the correct headers.

        :param section: section of the column
        :type section: int
        :param orientation: orientation of the view
        :type orientation: int
        :param role: role the index is being accessed with
        :type role: int
        :return: the label of the header
        :rtype: str
        """
        if (section == 0 and orientation == QtCore.Qt.Horizontal
            and role == QtCore.Qt.DisplayRole):
            return 'Name'

    def rowCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        """Returns the number of rows (i.e. the number of children) that are
        available for a given model index.

        :param parent: the index to be queried
        :type parent: QtCore.QModelIndex
        :return: the number of children of the current index
        :rtype: int
        """
        if not parent.isValid():
            item = self._root
        else:
            item = parent.internalPointer()
        return len(item.children)

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        """Returns the number of columns available for the given index, which
        in this model is fixed and corresponds to the number of sections.

        :param parent: the index to be queried
        :type parent: QtCore.QModelIndex
        :return: the number of columns of the current index
        :rtype: int
        """
        return 1

    def index(self, row, column, parent=QtCore.QModelIndex(), *args, **kwargs):
        """Allows views to go one level deeper in the index hierarchy of the
        model, by moving from the given parent index to its row-th child and
        accessing its column-th field. Invalid index allow to access the tree
        from its root, leaves do not allow to proceed any further.

        :param row: row of the new index (n-th child of the parent)
        :type row: int
        :param column: column of the new index
        :type column: int
        :param parent: parent index whence the view needs to go further
        :type parent: QtCore.QModelIndex
        :return: an index pointing to the desired child of the parent index
        :rtype: QtCore.QModelIndex
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            parent_item = self._root
        else:
            parent_item = parent.internalPointer()
        item = parent_item.children[row]
        return self.createIndex(row, column, item)

    def parent(self, index=QtCore.QModelIndex()):
        """Allows view to go one step backwards in the index hierarchy by
        calculating and returning the parent of the given index (if any) or
        returning an invalid index otherwise, such as in the case of the root
        index which obviously has no parent.

        :param index: the index whose parent must be determined
        :type index: QtCore.QModelIndex
        :return: an index pointing to the parent of the given index
        :rtype: QtCore.QModelIndex
        """
        if not index.isValid():
            return QtCore.QModelIndex()
        item = index.internalPointer()
        parent = item.parent
        if not parent:
            return QtCore.QModelIndex()
        row = parent.children.index(item)
        return self.createIndex(row, 0, item.parent)

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        """Allows views to query indices for the data they internally store,
        i.e. that part of property nodes which can be exposed to a tree view:
        the property name label.

        :param index: index where data must be extracted from
        :type index: QtCore.QModelIndex
        :param role: role the view is asking to access the index with
        :type role: int
        :return: a string representing the node label when the access role is
        QtCore.Qt.DisplayRole, otherwise the behaviour is undefined
        :rtype: object or None
        """
        item = index.internalPointer()
        section = index.column()
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return item.name
