
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QSizePolicy
from qtrangeslider import QLabeledRangeSlider

from Styling.Conversion import convert_mm_to_px, convert_percent_to_px_w, convert_px_to_mm


class Ruler(QLabeledRangeSlider):
    offsetsChanged = pyqtSignal(list)

    def __init__(self, values=(0, 15, 210), pageLeft=0, pageRight=0, parent=None, init=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setMinimum(0)
        self.setMaximum((21 - pageRight - pageLeft) * 10)

        self.setValue(list(values))
        if (pageLeft + pageRight) > 30:
            values = [values[0], 0, values[2]]
            self.setValue(values)
        if (pageLeft + pageRight) >= 210:
            raise ValueError("Page offsets are too big")

        self.setEdgeLabelMode(QLabeledRangeSlider.EdgeLabelMode.NoLabel)

        self.setMaximumWidth(convert_mm_to_px(self.maximum()))
        self.setMaximumHeight(convert_mm_to_px(10))
        self.sliderMoved.connect(self._on_slider_change)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def _on_slider_change(self):
        self.offsetsChanged.emit(self.value())

    def init(self, init):
        format = init.blockFormat()
        left_offset, indent, right_offset = [format.leftMargin(), format.textIndent(), format.rightMargin()]
        right_offset = 210 - convert_px_to_mm(right_offset)
        if right_offset < 0:
            right_offset = 0
        left_offset = convert_px_to_mm(left_offset)
        indent = convert_px_to_mm(indent)
        if indent == 0:
            indent = 1
        self.setValue([left_offset, indent, right_offset])
