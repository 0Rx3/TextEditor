from PyQt6.QtWidgets import QPushButton


class SwitchButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setStyleSheet("QPushButton:checked "
                           "{background-color: #000000; "
                           "color:#ffffff; "
                           "font-weight: bold; }")
