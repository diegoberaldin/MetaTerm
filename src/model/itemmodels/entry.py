__author__ = 'diego'

from PyQt4 import QtCore


class EntryModel(QtCore.QAbstractListModel):
    def __init__(self, termbase):
        super(EntryModel, self).__init__()
        self._entries = termbase.get_entries()
        self._language = None

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value
        self.modelReset.emit()

    def rowCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return len(self._entries)

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            entry = index.internalPointer()
            return entry.get_vedette(self.language)
