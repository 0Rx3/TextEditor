from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTextEdit

class EmittingEdit(QTextEdit):
    buttonPressed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        self.buttonPressed.emit(e.key())
        super().keyPressEvent(e)
