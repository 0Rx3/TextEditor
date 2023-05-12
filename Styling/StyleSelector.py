from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QComboBox


class StyleSelector(QWidget):
    styleIdChanged = pyqtSignal(int)

    def __init__(self, init=None, parent=None):
        super().__init__(parent)

        self.Selector = QComboBox()
        self.init(init, 0)

    def init(self, init, index):
        self.blockSignals(True)
        if init is not None:
            self.Selector.clear()
            for i in range(len(init)):
                self.Selector.addItem(init[i].name)
            if index < 0:
                index += 1
            elif index >= len(init):
                index -= 1
            self.Selector.setCurrentIndex(index)
        else:
            self.Selector.clear()
            self.Selector.addItems(["no styles passed"])
            self.Selector.setCurrentIndex(0)
        self.blockSignals(False)
