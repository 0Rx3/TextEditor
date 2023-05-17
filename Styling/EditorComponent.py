import time

from PyQt6.QtCore import Qt, QTimer, QThread
from PyQt6.QtGui import QTextCursor, QTextList, QTextOption, QTextBlock, QTextFormat, QTextListFormat, QAction
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QTextEdit, QGridLayout, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog

import json
from Exporter.ToMarkdown import convert_qt_markdown
from Styling.BlockStyle import BlockStyle
from Styling.BorderRuler import VBorderRuler, HBorderRuler
from Styling.Defaults import default_char_format, default_block_format, numeric_formats, _check_paradox, disc_marker, \
    convert_decimal_to_alpha, convert_decimal_to_roman, DefaultBlockStyle
from Styling.Highlighter import BlockHighlighter
from Styling.ListSettings.SideListStyler import SideListStyler
from Styling.Ruler import Ruler, convert_mm_to_px
from Styling.SideStyler import SideStyler
from Styling.Switches.SwitchButton import SwitchButton
from Styling.EmittingEdit import EmittingEdit
from Exporter.ToJSON import toJSON, fromJSON

timer_active = False


class EditorComponent(QWidget):
    def __init__(self):
        super().__init__()

        self.heightRuler = VBorderRuler()
        self.heightRuler.setDisabled(True)
        self.widthRuler = HBorderRuler()
        self.textRuler = Ruler()
        self.textEdit = EmittingEdit()

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
        self.styles = [DefaultBlockStyle.copy()]
        self.styles[0].name = "Default"
        self.textEdit.cursorPositionChanged.connect(self.force_update)
        self.sideStyler.init(self.styles[self.currentStyle], 0, self.styles)
        self.sideStyler.addedStyle.connect(self.addStyle)
        self.sideStyler.removedStyle.connect(self.removeStyle)
        self.sideStyler.changedId.connect(self._on_style_switch)
        self.sideStyler.anyChange.connect(self.force_update)

        self.sideListStyler = SideListStyler(self, self.styles, self.currentStyle)
        self.sideListStyler.changedParent.connect(self._on_parent_change)

        styler_layout = QVBoxLayout()
        styler_layout.addWidget(self.sideStyler)
        styler_layout.addWidget(self.sideListStyler)

        self.highlighter = BlockHighlighter(self.styles, self.blockStyles, self.textEdit.document(), EE=self.textEdit)

        self.HTMLExport = QPushButton("to .pdf", self)
        self.MDExport = QPushButton("to .md", self)
        self.JSONExport = QPushButton("to .json", self)
        self.HTMLExport.clicked.connect(self._to_pdf)
        self.MDExport.clicked.connect(self._to_md)
        self.JSONExport.clicked.connect(self._to_json)

        export_buttons = QHBoxLayout()
        export_buttons.addWidget(self.HTMLExport)
        export_buttons.addWidget(self.JSONExport)
        export_buttons.addWidget(self.MDExport)

        JSONDialogue = QFileDialog(self)
        JSONDialogue.setFileMode(QFileDialog.FileMode.ExistingFiles)
        JSONDialogue.setNameFilter("JSON (*.json)")
        JSONDialogue.fileSelected.connect(self._from_json)
        openJSONButton = QPushButton("from .json", self)
        openJSONButton.clicked.connect(JSONDialogue.open)

        export_buttons.addWidget(openJSONButton)

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
        self.highlighter.createdList.connect(self._list_handle)
        self.styles[0].changed.connect(self.highlight_wrap)
        self.update_margins((self.widthRuler.value(), self.textRuler.value()), self.getCurrentStyle())

        self.BoldAction = QAction("Bold", self)
        self.BoldAction.setCheckable(True)

    def update_margins(self, vals, style):
        borders, block = vals
        style.updateMarginLeft(block[0])
        style.updateMarginRight(self.textRuler.maximum() - block[2])
        style.updateTextIndent(block[1] - block[0])

    def blockAll(self):
        for st in self.styles:
            st.blockSignals(True)
        self.sideStyler.block(True)
        self.sideListStyler.block(True)


    def highlight_wrap(self):
        self.highlighter.rehighlight()

    def _list_handle(self, list: QTextList, block: QTextBlock):
        style = self.getBlockStyle(block)
        if style.parent is None:
            other_list = self._find_closest_style_list(style, block)
            if other_list is None or other_list[0] == list:
                return
            else:
                self._merge_list(other_list[0], list)
        else:
            parent_list = self._find_closest_parent_list(style, block)
            closest_sibling = self._find_closest_style_list(style, block)
            if parent_list is not None and parent_list[1] is not None and (closest_sibling is None or closest_sibling[0] is None or closest_sibling[1] < parent_list[1]):
                prefix = self._generate_block_prefix(parent_list[1])
                modified_format = list.format()
                modified_format.setNumberPrefix(prefix)
                list.setFormat(modified_format)
            elif closest_sibling is not None and closest_sibling[0] is not None:
                self._merge_list(closest_sibling[0], list)

    def _of_the_same_parent(self, block1, block2):
        p1 = self._find_closest_parent_list(self.getBlockStyle(block1), block1)
        p2 = self._find_closest_parent_list(self.getBlockStyle(block2), block2)
        return p1 == p2

    def _add_to_list_simple(self, style, block):
        listed = self._find_closest_style_list(style, block)
        consecutive_blocks = self.getConsecutiveBlocks(style)[1:]
        if listed is not None:
            for line in consecutive_blocks:
                for block in line:
                    listed[0].add(block)

    def _merge_list(self, l_to: QTextList, l_from: QTextList):
        length = l_from.count()
        for i in range(length):
            l_to.add(l_from.item(0))

    def _add_to_list_parent(self, style):
        first_id = self.blockStyles.index(self.styles.index(style))
        block = self.textEdit.document().findBlockByNumber(first_id)
        parent_list = self._find_closest_parent_list(style, block)
        if parent_list is not None:
            consecutive_blocks = self.getConsecutiveBlocks(style)
            fn = self._generate_numbering_lambda(parent_list[0])
            for line in consecutive_blocks:
                parent_index = self._find_closest_parent_list(style, line[0])[1]
                list = line[0].textList()
                cursor = QTextCursor(line[0])
                modified_format = style.listFormat()
                modified_format.setNumberPrefix(fn(parent_index))
                if list is None:
                    cursor.createList(modified_format)
                else:
                    for block in line[1:]:
                        list.add(block)

    def getCurrentStyle(self):
        return self.styles[self.currentStyle]

    def balanceBlocks(self, cursor: QTextCursor):
        current_block = cursor.block()
        block_num = current_block.blockNumber()
        while len(self.blockStyles) < self.textEdit.document().blockCount():
            self.blockStyles.insert(block_num, self.currentStyle)
        while len(self.blockStyles) > self.textEdit.document().blockCount():
            self.blockStyles.pop(block_num + 1)

    def getBlockStyle(self, block):
        return self.styles[self.blockStyles[block.blockNumber()]]

    def addStyle(self, style: BlockStyle):
        self.styles.append(style)
        self.styles[-1].changed.connect(self.highlight_wrap)
        self.currentStyle = self.sideStyler.Selector.currentRow() + 1
        blocks = self._get_blocks_between()
        self.sideStyler.init(self.styles[self.currentStyle], self.currentStyle, self.styles)
        for b in blocks:
            self.blockStyles[b] = self.currentStyle
        self.force_update()

    def removeStyle(self, num: int):
        if num == 0:
            return
        self.styles.pop(num)
        self.currentStyle = self.sideStyler.Selector.currentRow() - 1
        for i in range(len(self.blockStyles)):
            if self.blockStyles[i] == num:
                self.blockStyles[i] = self.currentStyle
        self.highlighter.highlightBlock("")

    def force_update(self):
        self.currentBlock = self.textEdit.textCursor().block()
        if len(self.blockStyles) != self.textEdit.document().blockCount():
            self.balanceBlocks(self.textEdit.textCursor())
        self.highlighter.blockStyles = self.blockStyles
        self.highlighter.styles = self.styles
        self.currentStyle = self.blockStyles[self.currentBlock.blockNumber()]
        self.sideStyler.init(self.styles[self.currentStyle], self.currentStyle, self.styles)
        self.sideListStyler.init(self.styles, self._get_possible_parents(self.currentBlock), self.currentStyle)


    def getConsecutiveBlocks(self, style):
        blocks = []
        app = []
        for num, i in enumerate(self.blockStyles):
            if self.styles[i] == style:
                block = self.textEdit.document().findBlockByNumber(num)
                app.append(block)
            else:
                if len(app) > 0:
                    blocks.append(app)
                    app = []
        if len(app) > 0:
            blocks.append(app)
        return blocks

    def _current_cursor_position(self):
        cursor = self.textEdit.textCursor()
        selection_pos = None
        if cursor.hasSelection():
            selection_pos = [cursor.selectionStart(), cursor.selectionEnd()]
        cursor_pos = cursor.position()
        return cursor_pos, selection_pos

    def _generate_numbering_lambda(self, list: QTextList):
        numbering_functions = [
            lambda x: str(x),
            lambda x: convert_decimal_to_alpha(x, True),
            lambda x: convert_decimal_to_alpha(x, False),
            lambda x: convert_decimal_to_roman(x, True),
            lambda x: convert_decimal_to_roman(x, False),
        ]
        list_fmt = list.format()
        list_style = list_fmt.style()
        if list_style in numeric_formats:
            prefix = list_fmt.numberPrefix()
            suffix = list_fmt.numberSuffix()
            if suffix == "":
                suffix = "."
            fn = numbering_functions[numeric_formats.index(list_style)]
            return lambda x: prefix + fn(x) + suffix
        else:
            prefix = disc_marker
            return lambda x: prefix

    def _generate_list_name(self, list):
        fn = self._generate_numbering_lambda(list)
        first = fn(0 + 1)
        first_text = list.item(0).text()
        last = fn(list.count())
        last_text = list.item(list.count() - 1).text()
        return first + " " + first_text + " ... " + last + " " + last_text

    def _generate_block_prefix(self, block):
        fn = self._generate_numbering_lambda(block.textList())
        return fn(block.textList().itemNumber(block) + 1)

    def _find_closest_style_list(self, style: BlockStyle, block: QTextBlock):
        blockId = block.blockNumber()
        while blockId > 0:
            blockId -= 1
            block = self.textEdit.document().findBlockByNumber(blockId)
            if self.getBlockStyle(block) == style and block.textList() is not None:
                return [block.textList(), block]
        return None

    def _find_closest_parent_list(self, style, block):
        style = style.parent
        if style is None:
            return None
        return self._find_closest_style_list(style, block)

    def _on_parent_change(self, num: int):
        if num < 0 or num == self.currentStyle or self.styles[num].listFormat() is None or self.styles[num].parent == self.getCurrentStyle():
            self.getCurrentStyle().updateParent(None)
            return
        self.getCurrentStyle().updateParent(self.styles[num])

    def _on_style_switch(self, styleId: int):
        if styleId > len(self.styles) - 1:
            return
        cp, sp = self._current_cursor_position()
        blocks_to_change = self._get_blocks_between()
        for blockId in blocks_to_change:
            self.blockStyles[blockId] = styleId
        #self._restore_cursor_position(cp, sp)

    def _get_blocks_between(self):
        cursor = self.textEdit.textCursor()
        start_position = cursor.selectionStart()
        end_position = cursor.selectionEnd()
        blocks = []
        for i in range(start_position, end_position):
            block = self.textEdit.document().findBlock(i)
            if block.blockNumber() not in blocks:
                blocks.append(block.blockNumber())
        if not blocks:
            blocks.append(self.currentBlock.blockNumber())
        return blocks

    def _to_pdf(self):
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName("tryout1.pdf")

        self.textEdit.document().print(printer)

    def _to_md(self):
        convert_qt_markdown(self.textEdit.document(), "tryout1.md")

    def _to_json(self):
        json_data = toJSON(self)
        with open("tryout1.json", "w") as f:
            json.dump(json_data, f)

    def _get_possible_parents(self, block):
        res = []
        for i in range(len(self.styles)):
            if self.styles[i].listFormat() is not None and self.styles[i] != self.getBlockStyle(block):
                found_list = self._find_closest_style_list(self.styles[i], block)
                if found_list is not None and found_list[0] is not None and not _check_paradox(self.styles[i], self.getBlockStyle(block)):
                    res.append(self._generate_list_name(found_list[0]))
                else:
                    res.append("Parent")
            elif self.styles[i].listFormat() is not None:
                res.append("self")
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

    def _from_json(self):
        with open("tryout1.json", "r") as f:
            json_data = json.load(f)
        fromJSON(json_data, self)



# TODO:
# Rework how list styles are applied: main problem - looking for a list constantly instead of passing it
# Add tables
# Add default styles
# Add more functions for decomposition?

