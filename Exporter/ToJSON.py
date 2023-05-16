from PyQt6.QtGui import QTextDocument, QTextCursor
from PyQt6.QtWidgets import QTextEdit

from Styling.BlockStyle import BlockStyle


def toJSON(edit):
    data = {
        "styles": [],
        "blockStyles": [],
        "text": []
    }
    for style in edit.styles:
        data["styles"].append(style.toJSON())
    for styleId in edit.blockStyles:
        data["blockStyles"].append(styleId)
    block_count = edit.textEdit.document().blockCount()
    for i in range(block_count):
        block = edit.textEdit.document().findBlockByNumber(i)
        data["text"].append(block.text())
    return data


def fromJSON(JSON, edit):
    edit.blockSignals(True)
    edit.textEdit.document().clear()
    edit.styles = []
    while edit.blockStyles:
        del edit.blockStyles[0]
    edit.currentStyle = 0
    for style in JSON["styles"]:
        app = BlockStyle()
        app.fromJSON(style)
        app.changed.connect(lambda x: edit.highlighter.highlightBlock(""))
        edit.styles.append(app)
    edit.textEdit.blockSignals(True)
    for num, text in enumerate(JSON["text"]):
        cursor = QTextCursor(edit.textEdit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        if num < len(JSON["blockStyles"]) - 1:
            cursor.insertBlock()
    edit.textEdit.blockSignals(False)
    for styleId in JSON["blockStyles"]:
        edit.blockStyles.append(styleId)
    edit.blockSignals(False)
    edit.force_update()