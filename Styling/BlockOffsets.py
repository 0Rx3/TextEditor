from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QSpinBox, QGridLayout

from Styling.Ruler import convert_mm_to_px, convert_px_to_mm


class BlockOffsets(QWidget):
    bottomOffsetChanged = pyqtSignal(int)
    topOffsetChanged = pyqtSignal(int)
    leftOffsetChanged = pyqtSignal(int)
    rightOffsetChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.BottomOffset = QSpinBox()
        self.TopOffset = QSpinBox()
        self.LeftOffset = QSpinBox()
        self.RightOffset = QSpinBox()

        ws = (self.LeftOffset, self.RightOffset)
        hs = (self.BottomOffset, self.TopOffset)
        for w in ws:
            w.setValue(0)
            w.setRange(0, 210)
            w.setFixedWidth(convert_mm_to_px(15))
            w.setEnabled(False)

        for h in hs:
            h.setValue(0)
            h.setRange(0, 100)
            h.setFixedWidth(convert_mm_to_px(15))

        self.BottomOffset.valueChanged.connect(self._on_bottom_change)
        self.TopOffset.valueChanged.connect(self._on_top_change)
        self.RightOffset.valueChanged.connect(self._on_right_change)
        self.LeftOffset.valueChanged.connect(self._on_left_change)

        layout = QGridLayout()
        layout.addWidget(self.LeftOffset, 1, 0)
        layout.addWidget(self.RightOffset, 1, 2)
        layout.addWidget(self.TopOffset, 0, 1)
        layout.addWidget(self.BottomOffset, 2, 1)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _on_bottom_change(self):
        self.bottomOffsetChanged.emit(self.BottomOffset.value())

    def _on_top_change(self):
        self.topOffsetChanged.emit(self.TopOffset.value())

    def _on_left_change(self):
        self.leftOffsetChanged.emit(self.LeftOffset.value())

    def _on_right_change(self):
        self.rightOffsetChanged.emit(self.RightOffset.value())

    def init(self, init):
        self.blockSignals(True)
        format = init.blockFormat()
        self.BottomOffset.setValue(convert_px_to_mm(format.bottomMargin()))
        self.TopOffset.setValue(convert_px_to_mm(format.topMargin()))
        self.LeftOffset.setValue(convert_px_to_mm(format.leftMargin()))
        self.RightOffset.setValue(convert_px_to_mm(format.rightMargin()))
        self.blockSignals(False)