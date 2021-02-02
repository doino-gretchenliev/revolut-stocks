from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class CheckableComboBox(QComboBox):

    # constructor
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.on_new_select)
        self.currentTextChanged.connect(self.on_selection_change)
        self.setModel(QStandardItemModel(self))

    def on_new_select(self, index):
        item = self.model().itemFromIndex(index)

        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def on_selection_change(self, value):
        for index in range(self.count()):
            item = self.model().item(index, 0)
            if item.checkState() == Qt.Checked:
                self.setCurrentIndex(index)
                return

        self.setCurrentIndex(0)

    def get_selected(self):
        selected = []
        for row in range(self.model().rowCount()):
            for column in range(self.model().columnCount()):
                item = self.model().item(row, column)
                if item.checkState() == Qt.Checked:
                    selected.append(item.text())

        return selected

    def addItems(self, texts, default):
        super(CheckableComboBox, self).addItems(texts)
        for row in range(self.model().rowCount()):
            for column in range(self.model().columnCount()):
                item = self.model().item(row, column)
                if item.text() == default:
                    item.setCheckState(Qt.Checked)
                    continue

                item.setCheckState(Qt.Unchecked)
