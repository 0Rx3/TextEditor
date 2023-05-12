from PyQt6.QtGui import QTextDocument, QTextList


def convert_qt_markdown(doc: QTextDocument, filename: str):
    current_index = 0
    output = []
    while current_index < doc.blockCount():
        block = doc.findBlockByNumber(current_index)
        text = block.text()
        if block.blockFormat().headingLevel():
            text = "#" * block.blockFormat().headingLevel() + " " + text
        elif block.textList() is not None:
            list = block.textList()
            indent = list.format().indent()
            non_numeric = [list.format().Style.ListDisc, list.format().Style.ListCircle, list.format().Style.ListSquare,]
            if list.format().style() in non_numeric:
                text = indent * "   " + "* " + text
            else:
                text = indent * "   " + "1. " + text
        elif current_index < doc.blockCount() - 1:
            text += "\\"
        output.append(text)
        current_index += 1

    with open(filename, "w") as file:
        file.write("\n".join(output))
        print("wrote file")

