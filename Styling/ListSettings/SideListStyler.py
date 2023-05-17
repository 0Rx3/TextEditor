from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextListFormat
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QSpinBox, QHBoxLayout

from Styling.BlockStyle import BlockStyle
from Styling.Defaults import _check_paradox, numeric_formats
from Styling.ListSettings.ListSuffPref import ListSuffPref
from Styling.ListSettings.ListType import ListType
from Styling.Ruler import convert_mm_to_px


class SideListStyler(QWidget):
    changedParent = pyqtSignal(int)
    changedListStyle = pyqtSignal(int)
    changedPrefix = pyqtSignal(str)
    changedSuffix = pyqtSignal(str)
    anyChange = pyqtSignal()

    def __init__(self, parent=None, init=None, index=0, parentNames=(), possibleParents=()):
        super().__init__(parent)

        self.Selector = QListWidget(self)
        self.SPModifier = ListSuffPref(self)
        self.IndentModifier = QSpinBox(self)
        self.TypeModifier = ListType(self)

        self.styles = []
        self.style = BlockStyle()
        self.parentIndex = 0

        layout = QVBoxLayout()
        sub = QHBoxLayout()
        sub.addWidget(self.IndentModifier)
        layout.addWidget(self.TypeModifier)
        sub.addWidget(self.SPModifier)
        layout.addLayout(sub)
        layout.addWidget(self.Selector)

        self.setLayout(layout)

        self.Selector.currentRowChanged.connect(self._on_current_list_changed)

        self.SPModifier.changedSuffix.connect(self._on_suffix_changed)
        self.SPModifier.changedPrefix.connect(self._on_prefix_changed)
        self.TypeModifier.listTypeChanged.connect(self._on_list_type_changed)

        self.IndentModifier.setRange(0, 10)
        self.IndentModifier.setMaximumWidth(convert_mm_to_px(15))
        self.IndentModifier.valueChanged.connect(self._on_indent_changed)

        self.setMaximumWidth(convert_mm_to_px(60))
        self.init(init, parentNames)

    def getParentIndex(self):
        style = self.style.parent
        if style is None:
            return -1
        else:
            for i in range(len(self.styles)):
                if self.styles[i] == style:
                    return i
            return -1

    def block(self, bool):
        self.blockSignals(bool)
        self.Selector.blockSignals(bool)
        self.IndentModifier.blockSignals(bool)
        self.SPModifier.blockSignals(bool)
        self.TypeModifier.blockSignals(bool)


    def init(self, init, parentNames, index=0):
        self.blockSignals(True)
        self.Selector.blockSignals(True)
        self.IndentModifier.blockSignals(True)
        if init is None:
            self.Selector.clear()
            self.Selector.addItem("None")
            self.Selector.setCurrentIndex(index)
            self.IndentModifier.setValue(0)
            self.setEnabled(False)
            return
        else:
            current_style = init[index]
            self.style = current_style
            self.styles = init
            self.parentIndex = self.getParentIndex()
            if current_style.listFormat() is not None:
                self.setEnabled(True)
                self.IndentModifier.setValue(self.style.listFormat().indent())
            else:
                self.setEnabled(False)
                self.IndentModifier.setValue(0)
            self.Selector.clear()
            if len(parentNames) > 0:
                for i in range(len(init)):
                    widgetItem = QListWidgetItem(parentNames[i])
                    widgetItem.setFont(self.styles[i].charFormat().font())
                    if parentNames[i] == self.styles[i].name or _check_paradox(self.styles[i], self.style):
                        font = widgetItem.font()
                        font.setStrikeOut(True)
                        widgetItem.setFont(font)
                    self.Selector.addItem(widgetItem)
            self.Selector.setCurrentRow(self.parentIndex)
            if self.style.listFormat() is not None and self.style.listFormat().Style in numeric_formats:
                self.SPModifier.setDisabled(True)
            else:
                self.SPModifier.setEnabled(True)
            self.SPModifier.init(self.style)
        self.blockSignals(False)
        self.Selector.blockSignals(False)
        self.IndentModifier.blockSignals(False)

    def _on_current_list_changed(self):
        try:
            self.style = self.styles[self.Selector.currentRow()]
        except IndexError:
            pass
        self._on_parent_changed()

    def _on_suffix_changed(self, suffix):
        self.style.updateListSuffix(suffix)

    def _on_prefix_changed(self, prefix):
        self.style.updateListPrefix(prefix)

    def _on_parent_changed(self):
        listed_styles = []
        for i in range(len(self.styles)):
            listed_styles.append(self.styles[i])
        self.changedParent.emit(self.Selector.currentRow())

    def _on_indent_changed(self):
        self.style.updateListIndent(self.IndentModifier.value())
        self.anyChange.emit()

    def _on_list_type_changed(self, num):
        self.style.updateListType(num)
        self.anyChange.emit()



