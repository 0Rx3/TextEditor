from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy

from Styling.Ruler import convert_mm_to_px
from Styling.Switches.SwitchButton import *


class FontStyles(QWidget):
    setBold = pyqtSignal(bool)
    setItalic = pyqtSignal(bool)
    setUnderline = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.BoldButton = SwitchButton("B")
        self.ItalicButton = SwitchButton("I")
        self.UnderlineButton = SwitchButton("U")

        layout = QHBoxLayout()

        self.buttons = (self.BoldButton, self.ItalicButton, self.UnderlineButton)
        for b in self.buttons:
            b.setMaximumWidth(convert_mm_to_px(8))
            layout.addWidget(b)

        layout.setSpacing(0)
        layout.setStretch(0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.BoldButton.clicked.connect(self._boldButtonPress)
        self.ItalicButton.clicked.connect(self._italicButtonPress)
        self.UnderlineButton.clicked.connect(self._underlineButtonPress)

    def _boldButtonPress(self):
        self.setBold.emit(self.BoldButton.isChecked())

    def _italicButtonPress(self):
        self.setItalic.emit(self.ItalicButton.isChecked())

    def _underlineButtonPress(self):
        self.setUnderline.emit(self.UnderlineButton.isChecked())

    def init(self, init):
        self.blockSignals(True)
        if init is not None:
            format = init.charFormat()
            bold, italic, underline = format.font().bold(), format.font().italic(), format.font().underline()
            self.BoldButton.setChecked(bold)
            self.ItalicButton.setChecked(italic)
            self.UnderlineButton.setChecked(underline)
        else:
            self.BoldButton.setChecked(False)
            self.ItalicButton.setChecked(False)
            self.UnderlineButton.setChecked(False)
        self.blockSignals(False)
