from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QLineEdit, QWidget, QLabel, QHBoxLayout

from Styling.Ruler import convert_mm_to_px


class ListSuffPref(QWidget):
    changedSuffix = pyqtSignal(str)
    changedPrefix = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._prefix = QLineEdit(self)
        self._suffix = QLineEdit(self)
        self._num_label = QLabel(self)

        self._suffix.setMaximumWidth(convert_mm_to_px(10))
        self._prefix.setMaximumWidth(convert_mm_to_px(10))
        self._num_label.setMaximumWidth(convert_mm_to_px(5))

        self._suffix.setPlaceholderText(".")

        self._prefix.textChanged.connect(self._on_prefix_changed)
        self._suffix.textChanged.connect(self._on_suffix_changed)

        self._suffix.setMaxLength(3)
        self._prefix.setMaxLength(3)

        layout = QHBoxLayout()

        layout.addWidget(self._prefix)
        layout.addWidget(self._num_label)
        layout.addWidget(self._suffix)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(self._prefix, Qt.AlignmentFlag.AlignRight)
        layout.setAlignment(self._suffix, Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)

        self._num_label.setText("1")

    def init(self, init):
        self.blockSignals(True)
        if init is None or init.listFormat() is None:
            self._prefix.setText("")
            self._suffix.setText("")
            self.setEnabled(False)
        else:
            self._prefix.setText(init.listFormat().numberPrefix())
            self._suffix.setText(init.listFormat().numberSuffix())
            self.setEnabled(True)
        self.blockSignals(False)

    def _on_prefix_changed(self):
        self.changedPrefix.emit(self._prefix.text())

    def _on_suffix_changed(self):
        self.changedSuffix.emit(self._suffix.text())


