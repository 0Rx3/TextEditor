from PyQt6.QtWidgets import QPushButton, QButtonGroup, QHBoxLayout


class SwitchButtonGroup(QButtonGroup):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setExclusive(True)
        self.buttonClicked.connect(self._onButtonClicked)
        self.buttons = []
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setStretch(0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_button(self, button: QPushButton):
        self.buttons.append(button)
        self.addButton(button)
        self.layout.addWidget(button)
        self.layout.setStretchFactor(button, 0)

    def _onButtonClicked(self, button: QPushButton):
        for b in self.buttons:
            if b != button:
                b.setChecked(False)
            else:
                b.setChecked(True)
