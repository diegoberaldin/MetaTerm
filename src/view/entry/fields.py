# -*- coding: utf-8 -*-

"""
.. currentmodule:: src.view.entry.fields

This module contains the definition of the fields that are used to represent
property assignments in the entry manipulation forms. In this respect each field
refers to a property and has a value, which is extracted from some input widget
provided by the Qt libraries.
"""

import os

from PyQt4 import QtCore, QtGui


class SelectFileInput(QtGui.QWidget):
    """Input widget used to select a resource from the local file system which
    basically consists of a disabled text field where the path is displayed
    and a browsing button. When the latter is clicked a dialog is opened to
    pick a resource from the local file system.
    """

    path_changed = QtCore.pyqtSignal()
    """Signal emitted when the path of the selected resource has changed.
    """

    def __init__(self, parent):
        """Constructor method.

        :param parent: reference to the parent widget
        :type parent: QtCore.QWidget
        :rtype: SelectFileInput
        """
        super(SelectFileInput, self).__init__(parent)
        self.setLayout(QtGui.QHBoxLayout(self))
        self._text_input = QtGui.QLineEdit(self)
        self._text_input.setEnabled(False)
        browse_button = QtGui.QPushButton('Browse', self)
        browse_button.clicked.connect(self._handle_button_clicked)
        self.layout().addWidget(self._text_input)
        self.layout().addWidget(browse_button)

    @QtCore.pyqtSlot()
    def _handle_button_clicked(self):
        """Private slot to be called when the button is clicked, after asking
        the user for a path to a local resource this is shown in the text
        input field and the ``path_changed`` signal is emitted.

        :rtype: None
        """
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose file',
                                                      os.path.expanduser('~'))
        if file_path:
            self._text_input.setText(file_path)
        else:
            self._text_input.setText('')
        self.path_changed.emit()

    @property
    def value(self):
        """Allows for subsequent form fields to access the selected value, i.e.
        the path that is shown in the text input field of the widget.

        :return: the selected (absolute) path to the resource
        :rtype: str
        """
        return self._text_input.text()

    @value.setter
    def value(self, value):
        self._text_input.setText(value)


class AbstractFormField(QtCore.QObject):
    """This class is used as an abstraction mechanism for all the fields that
    are displayed in the form for the creation of a new terminological entry, no
    matter whether they are implemented using custom or library classes.

    Fields are characterized by the defined property the locale (which is
    needed for language-level and term-level properties) and the defined lemma,
    moreover they hold a reference to the graphical widget used to collect the
    user input needed for their definition.

    All such fields must implement the ``value`` property, allowing a caller
    to access the value of the property that has been specified by the user
    through the GUI.
    """

    changed = QtCore.pyqtSignal()
    """Signal emitted when the value of the form field changes.
    """

    def __init__(self, prop, level, locale, lemma):
        """Constructor method.

        :param prop: reference to the property to be defined
        :type prop: Property
        :param level: level of the defined property
        :type level: str
        :param locale: representation of the locale of the language
        :type locale: str
        :param lemma: lemma of the defined term
        :type lemma: str
        :rtype: AbstractFormField
        """
        super(AbstractFormField, self).__init__()
        self.property = prop
        self.locale = locale
        self.level = level
        self.lemma = lemma
        self.widget = None

    @property
    def value(self):
        """This must be implemented by all subclasses to retrieve the property
        definition as it has been set by the end user via some GUI mechanism.

        :returns: the value of the property in the current field
        :rtype: object
        """
        raise NotImplementedError('Override me')

    @value.setter
    def value(self, value):
        """This must be implemented by all subclasses to set the property
        value via some GUI mechanism (depending on the widget).

        :param value: the new value of the property
        :type value: object
        :rtype: None
        """
        raise NotImplementedError('Override me')

    @QtCore.pyqtSlot(str)
    def update_lemma(self, lemma):
        """Use to automatically update the lemma of the field when a text input
        gets edited by the user via signal-slot mechanism.

        :param lemma: new lemma of the field
        :type lemma: str
        :rtype: None
        """
        self.lemma = lemma


class TextField(AbstractFormField):
    """Textual field to define simple textual properties. Note: the internal
    widget can be a QtGui.QLineEdit or a QtGui.QTextEdit.
    """

    def __init__(self, prop, level, parent, locale=None, lemma=None):
        super(TextField, self).__init__(prop, level, locale, lemma)
        self.widget = QtGui.QTextEdit(parent)
        self.widget.setMaximumHeight(30)
        # signal-slot connection
        self.widget.textChanged.connect(self.changed)

    @property
    def value(self):
        if hasattr(self.widget, 'toPlainText'):
            return self.widget.toPlainText()
        if hasattr(self.widget, 'text'):
            return self.widget.text()

    @value.setter
    def value(self, value):
        self.widget.setPlainText(value)


class PicklistField(AbstractFormField):
    """Field used to represent picklist properties, where the internal widget
    is a library combo box.
    """

    def __init__(self, prop, level, parent, locale=None, lemma=None):
        super(PicklistField, self).__init__(prop, level, locale, lemma)
        self.widget = QtGui.QComboBox(parent)
        model = QtGui.QStringListModel(prop.values)
        self.widget.setModel(model)
        # signal-slot connection
        self.widget.currentIndexChanged.connect(
            lambda unused_idx: self.changed.emit())

    @property
    def value(self):
        return self.widget.currentText()

    @value.setter
    def value(self, value):
        index = self.widget.model().stringList().index(value)
        self.widget.setCurrentIndex(index)


class FileField(AbstractFormField):
    """Field used to represent resources whose value is the path on the local
    system where such a resource can be found.
    """

    def __init__(self, prop, level, parent, locale=None, lemma=None):
        super(FileField, self).__init__(prop, level, locale, lemma)
        self.widget = SelectFileInput(parent)
        # signal-slot connection
        self.widget.path_changed.connect(self.changed)

    @property
    def value(self):
        return self.widget.value

    @value.setter
    def value(self, value):
        self.widget.value = value
