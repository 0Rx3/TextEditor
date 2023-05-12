from PyQt6.QtWidgets import QLabel


class Spacer(QLabel):
    def __init__(self, maxw=None, minw=None, maxh=None, minh=None, parent=None):
        super().__init__(parent)

        if maxw is not None:
            self.setMaximumWidth(maxw)
        if minw is not None:
            self.setMinimumWidth(minw)
        if maxh is not None:
            self.setMaximumHeight(maxh)
        if minh is not None:
            self.setMinimumHeight(minh)
