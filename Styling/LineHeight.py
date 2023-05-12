from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QSpinBox, QHBoxLayout


class LineHeight(QWidget):
    lineHeightChanged = pyqtSignal(float)

    def __init__(self, parent=None, init=None):
        super().__init__(parent)
        self.lineHeight = QSpinBox(self)
        self.lineHeight.setRange(50, 250)
        self.lineHeight.setSuffix("%")
        self.lineHeight.setSingleStep(10)

        self.init(init)

        self.lineHeight.valueChanged.connect(self._on_line_height_changed)

        layout = QHBoxLayout()
        layout.addWidget(self.lineHeight)
        self.setLayout(layout)

    def _on_line_height_changed(self):
        self.lineHeightChanged.emit(self.lineHeight.value())

    def init(self, init):
        self.blockSignals(True)
        if init is None or init.blockFormat().lineHeight() == 0:
            self.lineHeight.setValue(100)
        else:
            format = init.blockFormat()
            self.lineHeight.setValue(format.lineHeight())
        self.blockSignals(False)