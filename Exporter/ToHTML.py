from PyQt6.QtCore import QFile
from PyQt6.QtGui import QTextDocumentWriter
from PyQt6.QtWidgets import QPushButton


def to_html(doc):
    filename = "example.html"
    file = QFile(filename)
    if file.open(QFile.WriteOnly | QFile.Text):
        # Create a QTextDocumentWriter and set its format to HTML
        writer = QTextDocumentWriter(file)
        writer.setFormat("html")

        # Write the QTextDocument to the file
        writer.write(doc)

        # Close the file
        file.close()


class ToHTML(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("To HTML")

