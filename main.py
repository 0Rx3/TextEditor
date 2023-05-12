from PyQt6 import QtWidgets

from Styling.StylishEdit import StylishEdit


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        switch_button = StylishEdit()

        self.setCentralWidget(switch_button)


app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec()
