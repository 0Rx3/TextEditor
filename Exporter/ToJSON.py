from PyQt6.QtGui import QTextDocument, QTextCursor
from PyQt6.QtWidgets import QTextEdit

from Styling.BlockStyle import BlockStyle


def toJSON(edit):
    data = {
        "styles": [],
        "blockStyles": [],
        "text": [],
        "styleParent": []
    }
    for style in edit.styles:
        data["styles"].append(style.toJSON())
    for styleId in edit.blockStyles:
        data["blockStyles"].append(styleId)
    block_count = edit.textEdit.document().blockCount()
    for i in range(block_count):
        block = edit.textEdit.document().findBlockByNumber(i)
        data["text"].append(block.text())
    for style in edit.styles:
        data["styleParent"].append(edit.styles.index(style.parent) if style.parent is not None else -1)
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
    for num, styleId in enumerate(JSON["styleParent"]):
        if styleId == -1:
            edit.styles[num].parent = None
        else:
            edit.styles[num].parent = edit.styles[styleId]
    edit.blockSignals(False)
    edit.force_update()