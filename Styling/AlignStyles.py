from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QSizePolicy

from Styling.Ruler import convert_mm_to_px
from Styling.Switches import SwitchButton
from Styling.Switches.SwitchButtonGroup import SwitchButtonGroup


class AlignStyles(QWidget):
    alignChanged = pyqtSignal(Qt.AlignmentFlag)

    def __init__(self, parent=None, init=None):
        super().__init__(parent)

        self.AlignLeft = SwitchButton.SwitchButton("L")
        self.AlignCenter = SwitchButton.SwitchButton("C")
        self.AlignRight = SwitchButton.SwitchButton("R")
        self.AlignJustify = SwitchButton.SwitchButton("J")

        self.buttons = (self.AlignLeft, self.AlignCenter, self.AlignRight, self.AlignJustify)
        self.group = SwitchButtonGroup()

        for b in self.buttons:
            b.clicked.connect(self._on_clicked)
            b.setMaximumWidth(convert_mm_to_px(8))
            self.group.add_button(b)

        self.init(init)

        self.layout = self.group.layout
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setStretch(0, 0)

        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def _on_clicked(self):
        if self.AlignLeft.isChecked():
            self.alignChanged.emit(Qt.AlignmentFlag.AlignLeft)
        elif self.AlignCenter.isChecked():
            self.alignChanged.emit(Qt.AlignmentFlag.AlignCenter)
        elif self.AlignRight.isChecked():
            self.alignChanged.emit(Qt.AlignmentFlag.AlignRight)
        elif self.AlignJustify.isChecked():
            self.alignChanged.emit(Qt.AlignmentFlag.AlignJustify)

    def init(self, init):
        self.blockSignals(True)
        for b in self.buttons:
            b.setChecked(False)
        if init is None or init.blockFormat().alignment() == Qt.AlignmentFlag.AlignJustify:
            self.AlignJustify.setChecked(True)
        else:
            align = init.blockFormat().alignment()
            if align == Qt.AlignmentFlag.AlignLeft:
                self.AlignLeft.setChecked(True)
            elif align == Qt.AlignmentFlag.AlignCenter:
                self.AlignCenter.setChecked(True)
            elif align == Qt.AlignmentFlag.AlignRight:
                self.AlignRight.setChecked(True)
        self.blockSignals(False)
