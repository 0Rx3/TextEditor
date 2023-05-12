from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextListFormat, QTextCharFormat, \
    QTextBlockFormat, QTextTableFormat, QTextTableCellFormat

default_char_format = QTextCharFormat()
default_block_format = QTextBlockFormat()
default_list_format = QTextListFormat()
default_table_format = QTextTableFormat()
default_cell_format = QTextTableCellFormat()

default_char_format.setFontFamily("Times New Roman")
default_char_format.setFontPointSize(12)
default_char_format.setFontWeight(50)
default_char_format.setFontItalic(False)
default_char_format.setFontUnderline(False)
default_char_format.setFontStrikeOut(False)

default_block_format.setAlignment(Qt.AlignmentFlag.AlignJustify)

default_list_format.setStyle(QTextListFormat.Style.ListDecimal)
default_list_format.setIndent(0)


disc_marker = "•"

numeric_formats = [QTextListFormat.Style.ListDecimal, QTextListFormat.Style.ListLowerAlpha,
                   QTextListFormat.Style.ListUpperAlpha, QTextListFormat.Style.ListLowerRoman,
                   QTextListFormat.Style.ListUpperRoman]


def convert_decimal_to_roman(num, lower=False):
    res = ""
    while num > 0:
        if num >= 1000:
            res += "M"
            num -= 1000
        elif num >= 900:
            res += "CM"
            num -= 900
        elif num >= 500:
            res += "D"
            num -= 500
        elif num >= 400:
            res += "CD"
            num -= 400
        elif num >= 100:
            res += "C"
            num -= 100
        elif num >= 90:
            res += "XC"
            num -= 90
        elif num >= 50:
            res += "L"
            num -= 50
        elif num >= 40:
            res += "XL"
            num -= 40
        elif num >= 10:
            res += "X"
            num -= 10
        elif num >= 9:
            res += "IX"
            num -= 9
        elif num >= 5:
            res += "V"
            num -= 5
        elif num >= 4:
            res += "IV"
            num -= 4
        elif num >= 1:
            res += "I"
            num -= 1
    if lower:
        return res.lower()
    else:
        return res


def convert_decimal_to_alpha(num, lower=False):
    res = ""
    while num > 0:
        if num >= 26:
            res += "Z"
            num -= 26
        elif num >= 25:
            res += "Y"
            num -= 25
        elif num >= 24:
            res += "X"
            num -= 24
        elif num >= 23:
            res += "W"
            num -= 23
        elif num >= 22:
            res += "V"
            num -= 22
        elif num >= 21:
            res += "U"
            num -= 21
        elif num >= 20:
            res += "T"
            num -= 20
        elif num >= 19:
            res += "S"
            num -= 19
        elif num >= 18:
            res += "R"
            num -= 18
        elif num >= 17:
            res += "Q"
            num -= 17
        elif num >= 16:
            res += "P"
            num -= 16
        elif num >= 15:
            res += "O"
            num -= 15
        elif num >= 14:
            res += "N"
            num -= 14
        elif num >= 13:
            res += "M"
            num -= 13
        elif num >= 12:
            res += "L"
            num -= 12
        elif num >= 11:
            res += "K"
            num -= 11
        elif num >= 10:
            res += "J"
            num -= 10
        elif num >= 9:
            res += "I"
            num -= 9
        elif num >= 8:
            res += "H"
            num -= 8
        elif num >= 7:
            res += "G"
            num -= 7
        elif num >= 6:
            res += "F"
            num -= 6
        elif num >= 5:
            res += "E"
            num -= 5
        elif num >= 4:
            res += "D"
            num -= 4
        elif num >= 3:
            res += "C"
            num -= 3
        elif num >= 2:
            res += "B"
            num -= 2
        elif num >= 1:
            res += "A"
    if lower:
        return res.lower()
    else:
        return res


def _check_paradox(style1, style2):
    while style1 is not None:
        if style1 == style2:
            return True
        style1 = style1.parentNumeration

