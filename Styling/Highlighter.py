from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QSyntaxHighlighter, QTextCursor, QTextList, QTextBlock, QTextFormat
from PyQt6.QtWidgets import QApplication

from Styling.BlockStyle import BlockStyle
from Styling.Defaults import compare_block_format, compare_char_format, compare_list_format, numeric_formats


class BlockHighlighter(QSyntaxHighlighter):
    createdListAt = pyqtSignal(QTextBlock)
    createdList = pyqtSignal(QTextList, QTextBlock)

    def __init__(self, styles, blockStyles, parent=None, EE=None):
        super().__init__(parent)
        self.parent = parent
        self.styles = styles
        self.EE = EE
        self.blockStyles = blockStyles
        self.prev_blockStyles = []
        self.lastKey = None
        if EE is not None:
            self.EE.buttonPressed.connect(self._on_key_pressed)

    def init(self, init):
        self.blockSignals(True)
        self.styles = init
        self.blockSignals(False)

    def _on_key_pressed(self, key: int):
        self.lastKey = key

    def insideFunction(self, style: BlockStyle):
        cursor = QTextCursor(self.document())
        style_blocks = self.getConsecutiveBlocks(style)
        cursor.beginEditBlock()
        list_fmt = style.listFormat()
        for num, consecutive_blocks in enumerate(style_blocks):
            first_block = consecutive_blocks[0]
            last_block = consecutive_blocks[-1]
            cursor.setPosition(first_block.position())
            cursor.setPosition(last_block.position() + last_block.length() - 1, QTextCursor.MoveMode.KeepAnchor)
            if list_fmt is None:
                for b in consecutive_blocks:
                    self._remove_list(b)
                if not compare_block_format(cursor.blockFormat(), style.blockFormat()):
                    cursor.setBlockFormat(style.blockFormat())
                cursor.setCharFormat(style.charFormat())
            # check if not backspace
            elif self.lastKey != Qt.Key.Key_Backspace:
                cursor.createList(list_fmt)
                self.createdList.emit(cursor.currentList(), first_block)
                if not compare_char_format(cursor.charFormat(), style.charFormat()):
                    if first_block.position() > 0:
                        cursor.setPosition(first_block.position() - 1)
                    cursor.setPosition(last_block.position() + last_block.length() - 1, QTextCursor.MoveMode.KeepAnchor)
                    cursor.setCharFormat(style.charFormat())
                if not compare_block_format(cursor.blockFormat(), style.blockFormat()):
                    if first_block.position() > 0:
                        cursor.setPosition(first_block.position())
                    cursor.setPosition(last_block.position(), QTextCursor.MoveMode.KeepAnchor)
                    cursor.setBlockFormat(style.blockFormat())
        cursor.endEditBlock()

    def getConsecutiveBlocks(self, style):
        blocks = []
        app = []
        for num, i in enumerate(self.blockStyles):
            if self.styles[i] == style:
                block = self.document().findBlockByNumber(num)
                app.append(block)
            else:
                if len(app) > 0:
                    blocks.append(app)
                    app = []
        if len(app) > 0:
            blocks.append(app)
        return blocks

    def highlightBlock(self, text):
        for st in self.styles:
            self.insideFunction(st)

    def _remove_list(self, block):
        list = block.textList()
        if list is not None:
            list.remove(block)

    def getBlockStyle(self, blockId):
        return self.styles[self.blockStyles[blockId]]

    def _find_closest_style_list(self, style: BlockStyle, block: QTextBlock):
        cursor = QTextCursor(self.document())
        cursor.setPosition(block.position())
        blockId = block.blockNumber()
        while blockId > 0:
            blockId -= 1
            cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
            if self.getBlockStyle(blockId) == style and cursor.block().textList() is not None:
                return [block.textList(), blockId]
        return None

    def _add_to_list_simple(self, style, block):
        listed = self._find_closest_style_list(style, block)
        cursor = QTextCursor(self.document())
        if listed is None:
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.createList(style.listFormat())
        elif listed[0] is not None:
            listed = listed[0]
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            listed.add(cursor.block())

    def _find_block_in_list(self, listed: QTextList, blockId: int):
        for i in range(listed.count()):
            if listed.item(i).blockNumber() == blockId:
                return i
        return None

    def _add_to_list_parent(self, style, block):
        found_parent = self._find_closest_style_list(style.parent, block)
        found_child = self._find_closest_style_list(style, block)
        if found_parent is not None:
            par_list, par_index = found_parent
            if found_child is not None and found_child[1] > par_index:
                self._add_to_list_simple(style, block)
            else:
                cursor = QTextCursor(self.document())
                cursor.setPosition(block.position())
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                modified_format = style.listFormat()
                if par_list is not None and par_list.format().style() in numeric_formats:
                    par_list_index = self._find_block_in_list(par_list, par_index)
                    suffix = par_list.format().numberSuffix()
                    if suffix == "":
                        suffix = "."
                    parent_formatting = par_list.format().numberPrefix() + str(par_list_index + 1) + suffix
                    modified_format.setNumberPrefix(parent_formatting + style.listFormat().numberPrefix())
                cursor.createList(modified_format)

