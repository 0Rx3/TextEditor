from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QListWidget


class ListType(QListWidget):
    listTypeChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItem("Disc")
        self.addItem("Circle")
        self.addItem("Square")
        self.addItem("Decimal")
        self.addItem("Lower Alpha")
        self.addItem("Upper Alpha")
        self.addItem("Lower Roman")
        self.addItem("Upper Roman")

        self.currentRowChanged.connect(self._on_list_type_changed)

    def _on_list_type_changed(self):
        self.listTypeChanged.emit((self.currentRow() + 1) * -1)

    def init(self, init):
        self.blockSignals(True)
        format = init.listFormat()
        if format is None:
            self.setCurrentRow(0)
            self.setDisabled(True)
        else:
            self.setDisabled(False)
            self.setCurrentRow(init.blockFormat().style())
        self.blockSignals(False)