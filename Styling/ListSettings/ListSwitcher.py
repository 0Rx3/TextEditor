from PyQt6.QtCore import pyqtSignal

from Styling.Switches.SwitchButton import SwitchButton


class ListSwitcher(SwitchButton):
    switched = pyqtSignal()

    def __init__(self, parent=None, init=None):
        super().__init__("List", parent)

    def init(self, style):
        self.blockSignals(True)
        if style.listFormat() is None:
            self.setChecked(False)
        else:
            self.setChecked(True)
        self.blockSignals(False)

