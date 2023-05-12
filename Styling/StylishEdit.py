from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QTextList, QTextOption
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QTextEdit, QGridLayout, QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from Exporter.ToDocx import convert_qt_to_docx
from Exporter.ToMarkdown import convert_qt_markdown
from Styling.BlockStyle import BlockStyle
from Styling.BorderRuler import VBorderRuler, HBorderRuler
from Styling.Defaults import default_char_format, default_block_format, numeric_formats, _check_paradox, disc_marker
from Styling.ListSettings.SideListStyler import SideListStyler
from Styling.Ruler import Ruler, convert_mm_to_px
from Styling.SideStyler import SideStyler
from Styling.Switches.SwitchButton import SwitchButton


class StylishEdit(QWidget):
    def __init__(self):
        super().__init__()

        self.heightRuler = VBorderRuler()
        self.heightRuler.setDisabled(True)
        self.widthRuler = HBorderRuler()
        self.textRuler = Ruler()
        self.textEdit = QTextEdit()
        self.textEdit.setFixedWidth(convert_mm_to_px(210))
        self.textEdit.setMinimumHeight(convert_mm_to_px(150))
        self.widthRuler.valueChanged.connect(self._on_width_ruler_change)
        self.textRuler.valueChanged.connect(self._on_text_ruler_change)
        self.widthRuler.setMaximumHeight(convert_mm_to_px(10))
        self.sideStyler = SideStyler(self)
        self.NonPrintable = SwitchButton("NP", self)
        self.NonPrintable.setMaximumWidth(convert_mm_to_px(10))
        self.NonPrintable.setMaximumHeight(convert_mm_to_px(10))
        self.NonPrintable.clicked.connect(self._non_printables)

        self.currentBlock = self.textEdit.document().firstBlock()
        self.currentStyle = 0
        self.blockStyles = [0]
        self.styles = [BlockStyle(block_format=default_block_format, char_format=default_char_format, name="Default")]
        self.textEdit.cursorPositionChanged.connect(self._force_update)
        self.sideStyler.init(self.styles[self.currentStyle], 0, self.styles)
        self.sideStyler.addedStyle.connect(self.addStyle)
        self.sideStyler.removedStyle.connect(self.removeStyle)
        self.sideStyler.changedId.connect(self._on_style_switch)
        self.sideStyler.anyChange.connect(self._force_update)

        self.sideListStyler = SideListStyler(self, self.styles, self.currentStyle)
        self.sideListStyler.changedParent.connect(self._on_parent_change)

        styler_layout = QVBoxLayout()
        styler_layout.addWidget(self.sideStyler)
        styler_layout.addWidget(self.sideListStyler)

        self.HTMLExport = QPushButton("to .pdf", self)
        self.DOCXExport = QPushButton("to .docx", self)
        self.MDExport = QPushButton("to .md", self)
        self.HTMLExport.clicked.connect(self._to_pdf)
        self.DOCXExport.clicked.connect(self._to_docx)
        self.MDExport.clicked.connect(self._to_md)
        self.DOCXExport.setEnabled(False)

        export_buttons = QHBoxLayout()
        export_buttons.addWidget(self.HTMLExport)
        export_buttons.addWidget(self.DOCXExport)
        export_buttons.addWidget(self.MDExport)

        layout = QGridLayout()
        layout.addWidget(self.NonPrintable, 0, 0, 3, 1)
        layout.addWidget(self.heightRuler, 3, 0, 6, 1)
        layout.addWidget(self.widthRuler, 1, 1)
        layout.addWidget(self.textRuler, 2, 1)
        layout.addWidget(self.textEdit, 3, 1, 6, 1)
        layout.addLayout(styler_layout, 1, 2, 6, 1)
        layout.addLayout(export_buttons, 9, 1)
        layout.setAlignment(self.heightRuler, Qt.AlignmentFlag.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layout)

        self.setLayout(mainLayout)

        self.styles[0].changed.connect(lambda x: self.applyStyle(0))
        self.update_margins((self.widthRuler.value(), self.textRuler.value()), self.getCurrentStyle())

    def applyStyles(self):
        for num, style in enumerate(self.styles):
            self.applyStyle(num)

    def applyStyle(self, styleId: int):
        num = 0
        while num < len(self.blockStyles):
            if styleId == self.blockStyles[num]:
                self.applyStyleOnBlock(num)
            num += 1

    def update_margins(self, vals, style):
        borders, block = vals
        style.updateMarginLeft(block[0])
        style.updateMarginRight(self.textRuler.maximum() - block[2])
        style.updateIndent(block[1] - block[0])

    def getCurrentStyle(self):
        return self.styles[self.currentStyle]

    def balanceBlocks(self, cursor: QTextCursor):
        current_block = cursor.block()
        block_num = current_block.blockNumber()
        while len(self.blockStyles) < self.textEdit.document().blockCount():
            self.blockStyles.insert(block_num, self.currentStyle)
        while len(self.blockStyles) > self.textEdit.document().blockCount():
            self.blockStyles.pop(block_num + 1)

    def getBlockStyle(self, blockId):
        return self.styles[self.blockStyles[blockId]]

    def addStyle(self, style: BlockStyle):
        self.styles.append(style)
        self.currentStyle = self.sideStyler.Selector.currentRow() + 1
        blocks = self._get_blocks_between()
        self.sideStyler.init(self.styles[self.currentStyle], self.currentStyle, self.styles)
        for b in blocks:
            self.blockStyles[b] = self.currentStyle
        self.styles[len(self.styles) - 1].changed.connect(self.applyStyles)
        self._update_current_style()

    def removeStyle(self, num: int):
        if num == 0:
            return
        self.styles.pop(num)
        self.currentStyle = self.sideStyler.Selector.currentRow() - 1
        for i in range(len(self.blockStyles)):
            if self.blockStyles[i] == num:
                self.blockStyles[i] = self.currentStyle
        self._force_update()

    def applyStyleOnBlock(self, blockId):
        cursor = self.textEdit.textCursor()
        start_position = cursor.position()
        cursor.clearSelection()
        cursor.setPosition(self.textEdit.document().findBlockByNumber(blockId).position())
        style = self.getBlockStyle(cursor.blockNumber())
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        if cursor.block().textList() is None:
            cursor.setCharFormat(style.charFormat())
            cursor.clearSelection()
            cursor.setBlockFormat(style.blockFormat())
        else:
            cursor.mergeCharFormat(style.charFormat())
            cursor.clearSelection()
            cursor.mergeBlockFormat(style.blockFormat())
        self._list_handle(style, blockId)
        cursor.setPosition(start_position)
        self.textEdit.setTextCursor(cursor)

    def _force_update(self):
        self.currentBlock = self.textEdit.textCursor().block()
        self.balanceBlocks(self.textEdit.textCursor())
        self.currentStyle = self.blockStyles[self.currentBlock.blockNumber()]
        self.sideStyler.init(self.styles[self.currentStyle], self.currentStyle, self.styles)
        self.sideListStyler.init(self.styles, self._get_possible_parents(self.currentBlock.blockNumber()), self.currentStyle)
        self._update_current_style()

    def _update_current_style(self):
        self.currentStyle = self.blockStyles[self.textEdit.textCursor().blockNumber()]
        prev_vals_text, prev_vals_width = self.textRuler.value(), self.widthRuler.value()
        self.textRuler.blockSignals(True)
        self.widthRuler.blockSignals(True)
        self.textEdit.blockSignals(True)

        self.textRuler.init(self.getCurrentStyle())
        self.sideStyler.init(self.getCurrentStyle(), self.currentStyle, self.styles)
        self.sideListStyler.init(self.styles, self._get_possible_parents(self.currentBlock.blockNumber()), self.currentStyle)

        self.textRuler.setValue(prev_vals_text)
        self.widthRuler.setValue(prev_vals_width)

        cp, sp = self._current_cursor_position()
        self.applyStyles()
        self._restore_cursor_position(cp, sp)

        self.textRuler.blockSignals(False)
        self.widthRuler.blockSignals(False)
        self.textEdit.blockSignals(False)

    def _current_cursor_position(self):
        cursor = self.textEdit.textCursor()
        selection_pos = None
        if cursor.hasSelection():
            selection_pos = [cursor.selectionStart(), cursor.selectionEnd()]
        cursor_pos = cursor.position()
        return cursor_pos, selection_pos

    def _restore_cursor_position(self, cursor_pos, selection_pos):
        cursor = self.textEdit.textCursor()
        if selection_pos:
            start_pos, end_pos = selection_pos
            if cursor_pos == start_pos:
                cursor.setPosition(end_pos)
                cursor.setPosition(start_pos, QTextCursor.MoveMode.KeepAnchor)
            else:
                cursor.setPosition(start_pos)
                cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
            self.textEdit.setTextCursor(cursor)

    def _remove_list(self, blockId):
        cp, sp = self._current_cursor_position()
        cursor = self.textEdit.textCursor()
        cursor.setPosition(self.textEdit.document().findBlockByNumber(blockId).position())
        list = cursor.block().textList()
        if list is not None:
            list.remove(cursor.block())
        self._restore_cursor_position(cp, sp)

    def _find_closest_style_list(self, style: BlockStyle, blockId: int):
        while blockId > 0:
            blockId -= 1
            block = self.textEdit.document().findBlockByNumber(blockId)
            if self.getBlockStyle(blockId) == style:
                return [block.textList(), blockId]
        return None

    def _is_child_of_list(self, blockId, list):
        block = self.textEdit.document().findBlockByNumber(blockId)
        if block.textList() is not None and block.textList() == list:
            return True
        return False

    def _add_to_list_simple(self, style, blockId):
        listed = self._find_closest_style_list(style, blockId)
        block = self.textEdit.document().findBlockByNumber(blockId)
        cp, sp = self._current_cursor_position()
        cursor = self.textEdit.textCursor()
        if listed is None and style.listFormat() is not None:
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.createList(style.listFormat())
            self.textEdit.setTextCursor(cursor)
        elif listed[0] is not None and style.listFormat() is not None:
            listed = listed[0]
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            listed.add(cursor.block())
        self._restore_cursor_position(cp, sp)

    def _find_block_in_list(self, listed: QTextList, blockId: int):
        for i in range(listed.count()):
            if listed.item(i).blockNumber() == blockId:
                return i
        return None

    def _add_to_list_parent(self, style, blockId):
        block = self.textEdit.document().findBlockByNumber(blockId)
        found_parent = self._find_closest_style_list(style.parentNumeration, blockId)
        found_child = self._find_closest_style_list(style, blockId)
        if found_parent is not None:
            par_list, par_index = found_parent
            if found_child is not None and found_child[1] > par_index:
                self._add_to_list_simple(style, blockId)
            else:
                cp, sp = self._current_cursor_position()
                cursor = self.textEdit.textCursor()
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
                self.textEdit.setTextCursor(cursor)
                self._restore_cursor_position(cp, sp)

    def _list_handle(self, style: BlockStyle, blockId: int):
        listed = self._find_closest_style_list(style, blockId)
        if listed is not None and listed[0] is not None and style.parentNumeration is None:
            self._add_to_list_simple(style, blockId)
        if style.parentNumeration is not None and style.listFormat() is not None:
            self._add_to_list_parent(style, blockId)
        elif self.getBlockStyle(blockId) == style:
            c1 = self.getBlockStyle(blockId) != style or style.listFormat() is None
            if c1:
                self._remove_list(blockId)
            else:
                self._add_to_list_simple(style, blockId)

    def _on_parent_change(self, num: int):
        if num < 0 or num == self.currentStyle or self.styles[num].listFormat() is None or self.styles[num].parentNumeration == self.getCurrentStyle():
            self.getCurrentStyle().updateParent(None)
            return

        self.getCurrentStyle().updateParent(self.styles[num])

    def _get_blocks_between(self):
        blocks = []
        cursor = self.textEdit.textCursor()
        if not cursor.selection().isEmpty():
            start_position = cursor.selectionStart()
            end_position = cursor.selectionEnd()
            start_num = self.textEdit.document().findBlock(start_position).blockNumber()
            end_block = self.textEdit.document().findBlock(end_position).blockNumber()
            for i in range(start_num, end_block + 1):
                blocks.append(i)
        else:
            blocks = [cursor.blockNumber()]
        return blocks

    def _on_style_switch(self, styleId: int):
        if styleId > len(self.styles) - 1:
            return
        cp, sp = self._current_cursor_position()
        blocks_to_change = self._get_blocks_between()
        for blockId in blocks_to_change:
            self.blockStyles[blockId] = styleId
        self.applyStyle(styleId)
        self._restore_cursor_position(cp, sp)

    def _to_pdf(self):
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName("tryout1.pdf")

        self.textEdit.document().print(printer)

    def _to_docx(self):
        self.textEdit.blockSignals(True)

        cursor = self.textEdit.textCursor()
        cp, sp = self._current_cursor_position()
        cursor.setPosition(0)
        cursor.insertBlock()

        convert_qt_to_docx(self.textEdit.document(), "tryout1.docx")

        cursor.deletePreviousChar()

        self._restore_cursor_position(cp, sp)
        self.textEdit.blockSignals(False)

    def _to_md(self):
        convert_qt_markdown(self.textEdit.document(), "tryout1.md")

    def _create_list_name(self, blockId):
        found_list = self._find_closest_style_list(self.getBlockStyle(blockId), blockId + 1)
        res = None
        if found_list is not None and found_list[0] is not None:
            listed = found_list[0]
            if found_list[0].format().style() in numeric_formats:
                prefix = listed.format().numberPrefix()
                suffix = listed.format().numberSuffix()
                if suffix == "":
                    suffix = "."
                res = prefix + "1" + suffix + listed.item(0).text()[0:15]
                if listed.count() > 1:
                    res = prefix + "1" + suffix + listed.item(0).text()[0:5] + " ... " + prefix + str(
                        listed.count()) + suffix + listed.item(listed.count() - 1).text()[0:5]
            else:
                res = disc_marker + " " + listed.item(0).text()[0:15]
                if listed.count() > 1:
                    res = disc_marker + " " + listed.item(0).text()[0:5] + " ... " + disc_marker + " " + listed.item(listed.count() - 1).text()[0:5]
        return res

    def _get_possible_parents(self, blockId):
        res = []
        for i in range(len(self.styles)):
            if self.styles[i].listFormat() is not None and self.styles[i] != self.getBlockStyle(blockId):
                found_list = self._find_closest_style_list(self.styles[i], blockId)
                if found_list is not None and found_list[0] is not None and not _check_paradox(self.styles[i], self.getBlockStyle(blockId)):
                    res.append(self._create_list_name(found_list[0].item(0).blockNumber()))
                else:
                    res.append("Parent")
            else:
                res.append("No list")
        return res

    def _non_printables(self):
        current_option = self.textEdit.document().defaultTextOption()
        if self.NonPrintable.isChecked():
            current_option.setFlags(current_option.flags() | QTextOption.Flag.ShowTabsAndSpaces | QTextOption.Flag.ShowLineAndParagraphSeparators)
        else:
            current_option.setFlags(current_option.flags() & ~QTextOption.Flag.ShowTabsAndSpaces & ~QTextOption.Flag.ShowLineAndParagraphSeparators)
        self.textEdit.document().setDefaultTextOption(current_option)

    def _on_width_ruler_change(self):
        width_ruler_vals = list(self.widthRuler.value())
        text_ruler_vals = list(self.textRuler.value())
        if width_ruler_vals[0] != text_ruler_vals[0]:
            text_ruler_vals[0] = width_ruler_vals[0]
        if width_ruler_vals[1] != text_ruler_vals[2]:
            text_ruler_vals[2] = width_ruler_vals[1]
        if width_ruler_vals[0] >= text_ruler_vals[1]:
            text_ruler_vals[1] = width_ruler_vals[0]
        self.textRuler.setValue(text_ruler_vals)
        for style in self.styles:
            self.update_margins((width_ruler_vals, text_ruler_vals), style)
        self.sideStyler.init(self.getCurrentStyle(), self.currentStyle, self.styles)

    def _on_text_ruler_change(self):
        width_ruler_vals = list(self.widthRuler.value())
        text_ruler_vals = list(self.textRuler.value())
        if text_ruler_vals[0] < width_ruler_vals[0]:
            text_ruler_vals[0] = width_ruler_vals[0]
        if text_ruler_vals[1] > width_ruler_vals[1]:
            text_ruler_vals[1] = width_ruler_vals[1]
        elif text_ruler_vals[1] < width_ruler_vals[0]:
            text_ruler_vals[1] = width_ruler_vals[0]
        if text_ruler_vals[2] > width_ruler_vals[1]:
            text_ruler_vals[2] = width_ruler_vals[1]
        self.textRuler.setValue(text_ruler_vals)
        self.update_margins((width_ruler_vals, text_ruler_vals), self.getCurrentStyle())
        self.sideStyler.init(self.getCurrentStyle(), self.currentStyle, self.styles)


# TODO:
# Rework how list styles are applied: main problem - looking for a list constantly instead of passing it
# Add tables
# Add default styles
# Add more functions for decomposition?

