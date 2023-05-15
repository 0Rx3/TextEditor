# create container of QTextBlockFormat and QTextCharFormat

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QTextBlockFormat, QTextCharFormat, QTextListFormat, \
    QTextTableFormat, QTextFormat

from Styling.Ruler import convert_mm_to_px


class BlockStyle(QObject):
    blockFormatChanged = pyqtSignal(QTextBlockFormat)
    charFormatChanged = pyqtSignal(QTextCharFormat)
    listFormatChanged = pyqtSignal(QTextListFormat)
    tableFormatChanged = pyqtSignal(QTextTableFormat)
    changed = pyqtSignal(bool)

    def __init__(self, block_format=QTextBlockFormat(), char_format=QTextCharFormat(), list_format=None,
                 table_format=None, name="Default"):
        super().__init__()
        self.name = name
        self._blockFormat = block_format
        self._charFormat = char_format
        self._listFormat = list_format
        self._tableFormat = table_format
        self.parentNumeration = None
        self._backupListFormat = None
        self._backupTableFormat = None

    def blockFormat(self):
        return QTextBlockFormat(self._blockFormat)

    def charFormat(self):
        return QTextCharFormat(self._charFormat)

    def listFormat(self):
        if self._listFormat is None:
            return self._listFormat
        return QTextListFormat(self._listFormat)

    def tableFormat(self):
        if self._tableFormat is None:
            return self._tableFormat
        return QTextTableFormat(self._tableFormat)

    def setTableFormat(self, format: QTextTableFormat):
        self._tableFormat = format
        if format is not None:
            self._tableFormat = QTextTableFormat(format)
            self.tableFormatChanged.emit(self._tableFormat)
        self.changed.emit(True)

    def setListFormat(self, format: QTextListFormat):
        self._listFormat = format
        if format is not None:
            self._listFormat = QTextListFormat(format)
            self.listFormatChanged.emit(self._listFormat)
        self.changed.emit(True)

    def setBlockFormat(self, format: QTextBlockFormat):
        self._blockFormat = format
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def setCharFormat(self, format: QTextCharFormat):
        self._charFormat = format
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateFontFamily(self, font):
        family = font.family()
        self._charFormat.setFontFamily(family)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateIndent(self, indent):
        self._blockFormat.setTextIndent(convert_mm_to_px(indent))
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateMarginLeft(self, margin):
        self._blockFormat.setLeftMargin(convert_mm_to_px(margin))
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateMarginRight(self, margin):
        self._blockFormat.setRightMargin(convert_mm_to_px(margin))
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateMarginBottom(self, margin):
        self._blockFormat.setBottomMargin(convert_mm_to_px(margin))
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateMarginTop(self, margin):
        self._blockFormat.setTopMargin(convert_mm_to_px(margin))
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateTextAlignment(self, alignment):
        self._blockFormat.setAlignment(alignment)
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateTextBackgroundColor(self, color):
        self._charFormat.setBackground(color)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateTextColor(self, color):
        self._charFormat.setForeground(color)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateFontStyle(self, style):
        self._charFormat.setFontWeight(style.fontWeight())
        self._charFormat.setFontItalic(style.fontItalic())
        self._charFormat.setFontUnderline(style.fontUnderline())
        self._charFormat.setFontStrikeOut(style.fontStrikeOut())
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateFontSize(self, size):
        self._charFormat.setFontPointSize(size)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateBold(self, bool):
        font = self._charFormat.font()
        font.setBold(bool)
        self._charFormat.setFont(font)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateItalic(self, bool):
        self._charFormat.setFontItalic(bool)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateUnderline(self, bool):
        self._charFormat.setFontUnderline(bool)
        self.charFormatChanged.emit(self._charFormat)
        self.changed.emit(True)

    def updateHeadingLevel(self, num):
        self._blockFormat.setHeadingLevel(num)
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateLineHeight(self, num):
        self._blockFormat.setLineHeight(num, 1)
        self.blockFormatChanged.emit(self._blockFormat)
        self.changed.emit(True)

    def updateListStyle(self, num: int):
        if self._listFormat is None:
            self._listFormat = QTextListFormat()
        self._listFormat.setStyle(num)
        self.changed.emit(True)

    def updateListPrefix(self, text: str):
        if self._listFormat is None:
            return
        self._listFormat.setNumberPrefix(text)
        self.changed.emit(True)

    def updateListSuffix(self, text: str):
        if self._listFormat is None:
            return
        self._listFormat.setNumberSuffix(text)
        self.changed.emit(True)

    def turnOnOffList(self):
        if self._listFormat is None and self._backupListFormat is None:
            print("created")
            self._listFormat = QTextListFormat()
            self._listFormat.setStyle(QTextListFormat.Style.ListDecimal)
            self._listFormat.setIndent(0)
            self.parentNumeration = None
            self.changed.emit(True)
            return
        if self._listFormat is None:
            print("switched from backup")
            self._listFormat = self._backupListFormat
            self._blockFormat.setIndent(0)
            self._backupListFormat = None
        else:
            print("switched to backup")
            self._backupListFormat = self._listFormat
            self._blockFormat.setIndent(0)
            self._listFormat = None
        self.changed.emit(True)

    def updateParent(self, style):
        if self._listFormat is None:
            return
        if style is None or style.listFormat() is None:
            self.parentNumeration = None
            self._listFormat.setIndent(0)
            return
        self.parentNumeration = style
        self._listFormat.setIndent(self.parentNumeration.listFormat().indent() + 1)
        print("changedParent:", style)

    def copy(self):
        return BlockStyle(self.blockFormat(), self.charFormat(), self.listFormat(), self.tableFormat(),
                          self.name + "_copy")

    def updateName(self, name: str):
        self.name = name
        self.listChanged = 1
        self.changed.emit(True)

    def updateListIndent(self, num: int):
        if self._listFormat is None:
            return
        self._listFormat.setIndent(num)
        self.listChanged = 1
        self.changed.emit(True)

    def updateListType(self, num: int):
        if self._listFormat is None:
            return
        styles = [
            QTextListFormat.Style.ListDisc,
            QTextListFormat.Style.ListCircle,
            QTextListFormat.Style.ListSquare,
            QTextListFormat.Style.ListDecimal,
            QTextListFormat.Style.ListLowerAlpha,
            QTextListFormat.Style.ListUpperAlpha,
            QTextListFormat.Style.ListLowerRoman,
            QTextListFormat.Style.ListUpperRoman
        ]
        self._listFormat.setStyle(styles[num * -1 - 1])
        self.listChanged = 1

    def __str__(self):
        res = self.name + " -"
        has_list = self.listFormat() is not None
        has_table = self.tableFormat() is not None
        has_parent = self.parentNumeration is not None
        if has_list:
            res += " L:Y "
        else:
            res += " L:N "

        if has_table:
            res += " T:Y "
        else:
            res += " T:N "

        if has_parent:
            res += " P:" + self.parentNumeration.name + " "
        else:
            res += " P:N "

        return res
