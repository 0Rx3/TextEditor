# create container of QTextBlockFormat and QTextCharFormat

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QTextBlockFormat, QTextCharFormat, QTextListFormat, \
    QTextTableFormat, QFont
from Styling.Conversion import convert_mm_to_px


class BlockStyle(QObject):
    blockFormatChanged = pyqtSignal(QTextBlockFormat)
    charFormatChanged = pyqtSignal(QTextCharFormat)
    listFormatChanged = pyqtSignal(QTextListFormat)
    tableFormatChanged = pyqtSignal(QTextTableFormat)
    changed = pyqtSignal(bool)

    def __init__(self, block_format=QTextBlockFormat(), char_format=QTextCharFormat(), list_format=None,
                 table_format=None, name="Default", JSON=None):
        super().__init__()

        self.parent = None
        self._backupListFormat = None
        self._backupTableFormat = None

        if JSON is not None:
            self.fromJSON(JSON)
            return

        self.name = name
        self._blockFormat = block_format
        self._charFormat = char_format
        self._listFormat = list_format
        self._tableFormat = table_format

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

    def updateTextIndent(self, indent):
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
            self._listFormat = QTextListFormat()
            self._listFormat.setStyle(QTextListFormat.Style.ListDecimal)
            self._listFormat.setIndent(0)
            self.parent = None
            self.changed.emit(True)
            return
        if self._listFormat is None:
            self._listFormat = self._backupListFormat
            self._blockFormat.setIndent(0)
            self._backupListFormat = None
        else:
            self._backupListFormat = self._listFormat
            self._blockFormat.setIndent(0)
            self._listFormat = None
        self.changed.emit(True)

    def updateParent(self, style):
        self.changed.emit(True)
        if self._listFormat is None:
            return
        if style is None or style.listFormat() is None:
            self.parent = None
            self._listFormat.setIndent(0)
            return
        self.parent = style
        self._listFormat.setIndent(self.parent.blockFormat().indent() + 1)

    def copy(self):
        return BlockStyle(self.blockFormat(), self.charFormat(), self.listFormat(), self.tableFormat(),
                          self.name + "_copy")

    def updateName(self, name: str):
        self.name = name
        self.changed.emit(True)

    def updateListIndent(self, num: int):
        if self._listFormat is None:
            return
        self._blockFormat.setIndent(num)
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
        has_parent = self.parent is not None
        if has_list:
            res += " L:Y "
        else:
            res += " L:N "

        if has_table:
            res += " T:Y "
        else:
            res += " T:N "

        if has_parent:
            res += " P:" + self.parent.name + " "
        else:
            res += " P:N "

        return res

    def _char_to_JSON(self):
        return {
            "font": {
                "family": self.charFormat().font().family(),
                "size": self.charFormat().fontPointSize(),
                "bold": self.charFormat().font().bold(),
                "italic": self.charFormat().font().italic(),
                "underline": self.charFormat().font().underline(),
                "strikeout": self.charFormat().font().strikeOut()
            },
        }

    def _block_to_JSON(self):
        return {
            "alignment": self.blockFormat().alignment(),
            "textIndent": self.blockFormat().textIndent(),
            "heading": self.blockFormat().headingLevel(),
            "lineHeight": self.blockFormat().lineHeight(),
            "leftMargin": self.blockFormat().leftMargin(),
            "rightMargin": self.blockFormat().rightMargin(),
            "topMargin": self.blockFormat().topMargin(),
            "bottomMargin": self.blockFormat().bottomMargin()
        }

    def _list_to_JSON(self):
        if self.listFormat() is None:
            return None
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
        return {
            "indent": self.listFormat().indent(),
            "style": styles.index(self.listFormat().style()),
            "prefix": self.listFormat().numberPrefix(),
            "suffix": self.listFormat().numberSuffix()
        }

    def toJSON(self):
        return {
            "name": self.name,
            "charFormat": self._char_to_JSON(),
            "blockFormat": self._block_to_JSON(),
            "listFormat": self._list_to_JSON()
        }

    def _char_from_JSON(self, JSON):
        res = QTextCharFormat()
        font = QFont()
        font.setFamily(JSON["font"]["family"])
        font.setPointSize(JSON["font"]["size"])
        font.setBold(JSON["font"]["bold"])
        font.setItalic(JSON["font"]["italic"])
        font.setUnderline(JSON["font"]["underline"])
        font.setStrikeOut(JSON["font"]["strikeout"])
        res.setFont(font)
        return res

    def _block_from_JSON(self, JSON):
        res = QTextBlockFormat()
        alignments = {
            0: Qt.AlignmentFlag.AlignLeft,
            1: Qt.AlignmentFlag.AlignRight,
            132: Qt.AlignmentFlag.AlignHCenter,
            8: Qt.AlignmentFlag.AlignJustify,
        }
        print(JSON["alignment"])
        res.setAlignment(alignments[JSON["alignment"]])
        res.setTextIndent(JSON["textIndent"])
        res.setHeadingLevel(JSON["heading"])
        if JSON["lineHeight"] != 0:
            res.setLineHeight(JSON["lineHeight"], 1)
        res.setLeftMargin(JSON["leftMargin"])
        res.setRightMargin(JSON["rightMargin"])
        res.setTopMargin(JSON["topMargin"])
        res.setBottomMargin(JSON["bottomMargin"])
        return res

    def _list_from_JSON(self, JSON):
        if JSON is None:
            return None
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
        res = QTextListFormat()
        res.setIndent(JSON["indent"])
        res.setStyle(styles[JSON["style"]])
        res.setNumberPrefix(JSON["prefix"])
        if JSON["suffix"] != "":
            res.setNumberSuffix(JSON["suffix"])
        return res

    def fromJSON(self, JSON):
        self.name = JSON["name"]
        self._charFormat = self._char_from_JSON(JSON["charFormat"])
        self._blockFormat = self._block_from_JSON(JSON["blockFormat"])
        self._listFormat = self._list_from_JSON(JSON["listFormat"])
        self.changed.emit(True)