from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy, QListWidget, \
    QListWidgetItem, QLineEdit

from Styling.AlignStyles import AlignStyles
from Styling.BlockOffsets import BlockOffsets
from Styling.BlockStyle import BlockStyle
from Styling.FontChanger import FontChanger
from Styling.FontStyles import FontStyles
from Styling.HeadingLevel import HeadingLevel
from Styling.LineHeight import LineHeight
from Styling.ListSettings.ListSwitcher import ListSwitcher
from Styling.Ruler import convert_mm_to_px


class SideStyler(QWidget):
    addedStyle = pyqtSignal(BlockStyle)
    removedStyle = pyqtSignal(int)
    changedId = pyqtSignal(int)
    anyChange = pyqtSignal()
    movedStyles = pyqtSignal(list)

    def __init__(self, parent=None, init=BlockStyle()):
        super().__init__(parent)

        self.Selector = QListWidget(self)
        self.Selector.setMaximumHeight(convert_mm_to_px(40))
        self.StyleName = QLineEdit(self)
        self.RemovalButton = QPushButton("-", self)
        self.AdditionButton = QPushButton("+", self)
        self.AlignButtons = AlignStyles(self)
        self.FontButtons = FontStyles(self)
        self.FontChanger = FontChanger(self)
        self.FontChanger.setFixedHeight(convert_mm_to_px(10))
        self.HeadingLevel = HeadingLevel(self)
        self.BlockOffsets = BlockOffsets(self)
        self.LineHeight = LineHeight(self)
        self.ListSwitcher = ListSwitcher(self)
        self.style = init

        self.RemovalButton.clicked.connect(self._remove_button_press)
        self.AdditionButton.clicked.connect(self._add_button_press)

        selector_row = QVBoxLayout()
        selector_button_row = QHBoxLayout()
        selector_button_row.addWidget(self.AdditionButton)
        selector_button_row.addWidget(self.RemovalButton)
        selector_row.addLayout(selector_button_row)
        selector_row.addWidget(self.Selector)
        selector_row.addWidget(self.StyleName)
        selector_row.setSpacing(0)

        button_row = QHBoxLayout()
        button_row.addWidget(self.AlignButtons)
        button_row.addWidget(self.FontButtons)
        button_row.setSpacing(0)

        layout = QVBoxLayout()
        layout.addLayout(selector_row)
        layout.addLayout(button_row)
        layout.addWidget(self.FontChanger)
        layout.addWidget(self.BlockOffsets)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.LineHeight)
        layout.addWidget(self.HeadingLevel)
        layout.addWidget(self.ListSwitcher)
        layout.setSpacing(0)
        layout.setStretch(0, 0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMaximumWidth(convert_mm_to_px(60))

        self.FontButtons.setBold.connect(self._bold_button_press)
        self.FontButtons.setItalic.connect(self._italic_button_press)
        self.FontButtons.setUnderline.connect(self._underline_button_press)

        self.FontChanger.fontFamilyChanged.connect(self._font_family_changed)
        self.FontChanger.fontSizeChanged.connect(self._font_size_changed)

        self.AlignButtons.alignChanged.connect(self._align_changed)

        self.Selector.currentRowChanged.connect(self._selector_changed)

        self.BlockOffsets.topOffsetChanged.connect(self._top_offset_changed)
        self.BlockOffsets.bottomOffsetChanged.connect(self._bottom_offset_changed)
        self.BlockOffsets.leftOffsetChanged.connect(self._left_offset_changed)
        self.BlockOffsets.rightOffsetChanged.connect(self._right_offset_changed)

        self.HeadingLevel.headingLevelChanged.connect(self._heading_level_changed)
        self.LineHeight.lineHeightChanged.connect(self._line_height_changed)

        self.StyleName.textChanged.connect(self._style_name_changed)

        self.ListSwitcher.clicked.connect(self._list_switched)

    def block(self, bool):
        self.AlignButtons.blockSignals(bool)
        self.FontButtons.blockSignals(bool)
        self.FontChanger.blockSignals(bool)
        self.HeadingLevel.blockSignals(bool)
        self.BlockOffsets.blockSignals(bool)
        self.LineHeight.blockSignals(bool)
        self.ListSwitcher.blockSignals(bool)
        self.Selector.blockSignals(bool)
        self.StyleName.blockSignals(bool)
        self.blockSignals(bool)

    def init(self, style, styleId, init):
        self.block(True)
        if self.Selector.count() < styleId + 1:
            self.Selector.addItem(style.name)
        self.style = style

        self.Selector.clear()
        for st in init:
            widgetItem = QListWidgetItem(st.name)
            widgetItem.setFont(st.charFormat().font())
            self.Selector.addItem(widgetItem)

        self.Selector.setCurrentRow(styleId)
        self.StyleName.setText(style.name)
        self.AlignButtons.init(self.style)
        self.FontButtons.init(self.style)
        self.BlockOffsets.init(self.style)
        self.LineHeight.init(self.style)
        self.HeadingLevel.init(self.style)
        self.ListSwitcher.init(self.style)
        self.FontChanger.init([self.style.charFormat().font(), self.style.charFormat().font().pointSize()])
        self.block(False)

    def _add_button_press(self):
        self.addedStyle.emit(self.style.copy())
        self.anyChange.emit()

    def _remove_button_press(self):
        self.removedStyle.emit(self.Selector.currentRow())
        self.anyChange.emit()

    def _heading_level_change(self):
        self.style.updateHeadingLevel(self.HeadingLevel.value())
        self.anyChange.emit()

    def _bold_button_press(self, bool):
        self.style.updateBold(bool)
        self.anyChange.emit()

    def _italic_button_press(self, bool):
        self.style.updateItalic(bool)
        self.anyChange.emit()

    def _underline_button_press(self, bool):
        self.style.updateUnderline(bool)
        self.anyChange.emit()

    def _font_family_changed(self, font: QFont):
        self.style.updateFontFamily(font)
        self.anyChange.emit()

    def _font_size_changed(self, size: float):
        self.style.updateFontSize(size)
        self.anyChange.emit()

    def _selector_changed(self, l):
        self.changedId.emit(self.Selector.currentRow())
        self.anyChange.emit()

    def _align_changed(self, align):
        self.style.updateTextAlignment(align)
        self.anyChange.emit()

    def _heading_level_changed(self, num: int):
        self.style.updateHeadingLevel(num)
        self.anyChange.emit()

    def _top_offset_changed(self, num: int):
        self.style.updateMarginTop(num)
        self.anyChange.emit()

    def _bottom_offset_changed(self, num: int):
        self.style.updateMarginBottom(num)
        self.anyChange.emit()

    def _line_height_changed(self, num: float):
        self.style.updateLineHeight(num)
        self.anyChange.emit()

    def _left_offset_changed(self, num: int):
        self.style.updateMarginLeft(num)
        self.anyChange.emit()

    def _right_offset_changed(self, num: int):
        self.style.updateMarginRight(num)
        self.anyChange.emit()

    def _list_style_changed(self, num: int):
        self.style.updateListStyle(num)
        self.anyChange.emit()

    def _list_switched(self):
        self.style.turnOnOffList()
        self.anyChange.emit()

    def _style_name_changed(self):
        self.style.updateName(self.StyleName.text())
        self.anyChange.emit()