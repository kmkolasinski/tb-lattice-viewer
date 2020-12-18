from typing import List, Optional
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from natsort import natsorted


class ListWidget(QListWidget):
    def sizeHint(self):
        s = QSize()
        s.setHeight(super(ListWidget, self).sizeHint().height())
        s.setWidth(self.sizeHintForColumn(0))
        return s


class ParamsListWidget(QWidget):
    """A list with searchable items, item can be deleted"""

    def __init__(
        self,
        elements: List[str],
        allow_add: bool = True,
        allow_delete: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        mainLayout = QVBoxLayout()
        self.itemsList = ListWidget()

        elements = natsorted(elements, key=lambda w: w.lower() if w is not None else w)

        self.default_items = elements
        mainLayout.addWidget(self.itemsList)

        hLayout = QHBoxLayout()
        self.nameEdit = QLineEdit()
        self.addItemButton = QPushButton("+")
        self.deleteItemButton = QPushButton("-")
        hLayout.addWidget(self.nameEdit)
        if allow_add:
            hLayout.addWidget(self.addItemButton)
        if allow_delete:
            hLayout.addWidget(self.deleteItemButton)

        mainLayout.addLayout(hLayout)
        self.setLayout(mainLayout)
        self.addItemButton.pressed.connect(self.addEditItem)
        self.deleteItemButton.pressed.connect(self.removeSelectedItems)
        self.nameEdit.textChanged.connect(self.searchForItem)
        self.updateList()

    def updateList(self):
        self.itemsList.clear()
        for elem in self.default_items:
            item = QListWidgetItem(elem)
            item.setForeground(QColor("green"))
            self.itemsList.addItem(item)

    def removeSelectedItems(self):
        listItems = self.itemsList.selectedItems()
        if not listItems:
            return
        for item in listItems:
            self.itemsList.takeItem(self.itemsList.row(item))

    @property
    def names(self) -> List[str]:
        return [self.itemsList.item(i).text() for i in range(self.itemsList.count())]

    @property
    def normalizedNames(self) -> List[str]:
        return [n.lower() for n in self.names]

    def hasWordInNames(self, word: str) -> bool:
        return word.lower() in self.normalizedNames

    def hasAnyOfWordsInNames(self, words: List[str]) -> bool:
        return any(self.hasWordInNames(word) for word in words)

    def findInNames(self, word: str) -> str:
        word = word.lower()
        for n, normed_n in zip(self.names, self.normalizedNames):
            if word in normed_n:
                return n
        return ""

    def findInNamesWords(self, words: List[str]) -> Optional[str]:
        matches = [self.findInNames(w) for w in words]
        matches = [m for m in matches if m != ""]
        if len(matches) > 0:
            return matches[0]
        return None

    @property
    def searchText(self) -> str:
        return self.nameEdit.text()

    def searchForItem(self):
        searchWords = self.searchText.lower().split(" ")
        matchedItems = []
        for i in range(self.itemsList.count()):
            item: QListWidgetItem = self.itemsList.item(i)
            itemText = item.text().lower()
            item.setSelected(False)
            if all([sw in itemText for sw in searchWords]):
                item.setHidden(False)
                matchedItems.append(item)
            else:
                item.setHidden(True)

        if len(matchedItems) == 1:
            matchedItems[0].setSelected(True)

    def addEditItem(self):
        self.addItem(self.nameEdit.text())

    def addItem(self, text: str):
        if text == "":
            return

        current_items = []
        for i in range(self.itemsList.count()):
            item: QListWidgetItem = self.itemsList.item(i)
            current_items.append(item.text())

        if text not in current_items:
            self.itemsList.addItem(text)

    def removeItem(self, text: str):
        if text in self.default_items:
            return

        for i in range(self.itemsList.count()):
            item: QListWidgetItem = self.itemsList.item(i)
            if item.text() == text:
                self.itemsList.takeItem(item)

    def selectedItem(self) -> Optional[str]:
        selItems = self.itemsList.selectedItems()
        if not selItems:
            return None
        return selItems[0].text()

    def selectItem(self, text: str):

        if text == "":
            self.searchForItem()
            return

        for i in range(self.itemsList.count()):
            item: QListWidgetItem = self.itemsList.item(i)
            item.setSelected(False)
            item.setHidden(False)
            if item.text() == text:
                item.setSelected(True)
                self.nameEdit.setFocus()


class ParamsListDialog(QDialog, ParamsListWidget):
    def __init__(
        self,
        elements: List[str],
        allow_add: bool = True,
        allow_delete: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(
            elements, allow_add=allow_add, allow_delete=allow_delete, *args, **kwargs
        )
        self.itemsList.mouseDoubleClickEvent = lambda event: self.accept()

    def showDialog(self, text: str = None) -> Optional[str]:
        self.selectItem(text)
        if self.exec_():
            return self.selectedItem()
        else:
            return None

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            self.accept()

        if e.key() == Qt.Key_Escape:
            self.reject()


class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet(
            "QToolButton { border: none; font-weight: bold;}"
        )
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setFrameShape(QFrame.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(300)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(300)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class VectorWidget(QWidget):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.v1x = QDoubleSpinBox()
        self.v1y = QDoubleSpinBox()

        self.v1x.setValue(1)
        self.v1y.setValue(0)
        self.v1x.setMaximumWidth(100)
        self.v1y.setMaximumWidth(100)
        self.v1x.setDecimals(5)
        self.v1y.setDecimals(5)
        self.v1x.setSingleStep(0.001)
        self.v1y.setSingleStep(0.001)

        self.v1x.setMaximum(10000)
        self.v1x.setMinimum(-10000)

        self.v1y.setMaximum(10000)
        self.v1y.setMinimum(-10000)

        self.nameLabel = QLabel()
        self.setName(name)

        h = QHBoxLayout()
        h.addWidget(self.nameLabel)
        h.addWidget(self.v1x)
        h.addWidget(self.v1y)
        h.setContentsMargins(0, 0, 0, 0)
        self.setLayout(h)

    def setName(self, name):
        self.name = name
        self.nameLabel.setText(f"<b>{name}</b> = ")

    def setValue(self, xy):
        self.v1x.setValue(xy[0])
        self.v1y.setValue(xy[1])

    def getValue(self):
        return self.v1x.value(), self.v1y.value()

    def toFortranListStr(self) -> str:
        x, y = self.v1x.value(), self.v1y.value()
        return f"(/{x}, {y}/)"

    def vec(self) -> QVector3D:
        return QVector3D(self.v1x.value(), self.v1y.value(), 0.0)

    def asTuple(self):
        return self.v1x.value(), self.v1y.value()

    def getStepIndexAt(self, x, y):
        if self.v1x.value() == 0:
            sx = 0
        else:
            sx = round(x / self.v1x.value())

        if self.v1y.value() == 0:
            sy = 0
        else:
            sy = round(y / self.v1y.value())

        return sx, sy
