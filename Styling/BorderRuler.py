from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QSizePolicy
from qtrangeslider import QLabeledRangeSlider

from Styling.Ruler import convert_mm_to_px


class VBorderRuler(QLabeledRangeSlider):
    offsetsChanged = pyqtSignal(list)

    def __init__(self, values=(0, 297), pageBottom=0, pageUp=0, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)
        if (pageBottom + pageUp) >= 29.7:
            raise ValueError("Page offsets are too big")
        self.setMinimum(0)
        self.setMaximum((29.7 - pageBottom - pageUp) * 10)
        self.setValue(list(values))
        self.setMaximumHeight(convert_mm_to_px(self.maximum()))
        self.setEdgeLabelMode(QLabeledRangeSlider.EdgeLabelMode.NoLabel)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def on_value_changed(self):
        self.offsetsChanged.emit(self.value())


class HBorderRuler(QLabeledRangeSlider):
    offsetsChanged = pyqtSignal(list)

    def __init__(self, values=(0, 210), pageLeft=0, pageRight=0, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        if (pageLeft + pageRight) >= 21:
            raise ValueError("Page offsets are too big")
        self.setMinimum(0)
        self.setMaximum((21 - pageLeft - pageRight) * 10)
        self.setValue(list(values))
        self.setMaximumWidth(convert_mm_to_px(self.maximum()))
        self.setMaximumHeight(convert_mm_to_px(10))
        self.setEdgeLabelMode(QLabeledRangeSlider.EdgeLabelMode.NoLabel)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def on_value_changed(self):
        self.offsetsChanged.emit(self.value())
