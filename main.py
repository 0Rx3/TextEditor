from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from Styling.EditorComponent import EditorComponent


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        edit = EditorComponent()

        self.setCentralWidget(edit)


app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec()
