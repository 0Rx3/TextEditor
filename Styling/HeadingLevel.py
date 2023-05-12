from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QSpinBox


class HeadingLevel(QSpinBox):
    headingLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 6)
        self.setValue(0)
        self.setPrefix("H")
        self.valueChanged.connect(self._on_heading_level_changed)

    def _on_heading_level_changed(self):
        self.headingLevelChanged.emit(self.value())

    def init(self, init):
        self.blockSignals(True)
        if init is None:
            self.setValue(0)
        else:
            self.setValue(init.blockFormat().headingLevel())
        self.blockSignals(False)