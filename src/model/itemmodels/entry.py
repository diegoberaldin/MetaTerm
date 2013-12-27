__author__ = 'diego'

from PyQt4 import QtCore


class EntryModel(QtCore.QAbstractListModel):
    def __init__(self, termbase):
        super(EntryModel, self).__init__()
        self._entries = termbase.entries
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
        if index.isValid():
            entry = self.get_entry(index)
            if role == QtCore.Qt.DisplayRole:
                return entry.get_vedette(self.language)

    def get_entry(self, index):
        if index.row() < self.rowCount():
            return self._entries[index.row()]
