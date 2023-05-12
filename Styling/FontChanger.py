from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFontComboBox, QSpinBox

from Styling.Ruler import convert_mm_to_px


class FontChanger(QWidget):
    fontFamilyChanged = pyqtSignal(QFont)
    fontSizeChanged = pyqtSignal(float)

    def __init__(self, parent=None, init=None):
        super().__init__(parent)
        self.fontFamily = QFontComboBox()
        self.fontFamily.currentFontChanged.connect(self._on_font_family_changed)
        self.fontFamily.setWritingSystem(QFontDatabase.WritingSystem.Cyrillic)
        self.fontSize = QSpinBox()
        self.fontSize.setRange(4, 100)

        layout = QHBoxLayout()
        layout.addWidget(self.fontSize)
        layout.addWidget(self.fontFamily)

        self.fontSize.setMaximumWidth(convert_mm_to_px(15))
        self.fontSize.valueChanged.connect(self._on_font_size_changed)

        self.init(init)

        layout.setSpacing(0)
        layout.setStretch(0, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def init(self, init):
        self.blockSignals(True)
        if init is None:
            self.fontFamily.setFont(QFont("Times New Roman"))
            self.fontSize.setValue(12)
        else:
            self.fontFamily.setFont(init[0])
            self.fontFamily.setCurrentText(init[0].family())
            self.fontSize.setValue(init[1])
        self.blockSignals(False)

    def _on_font_family_changed(self):
        self.fontFamilyChanged.emit(self.fontFamily.currentFont())

    def _on_font_size_changed(self):
        self.fontSizeChanged.emit(self.fontSize.value())
