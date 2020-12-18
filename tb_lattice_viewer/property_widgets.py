from typing import Any, List, Optional
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from tb_lattice_viewer.presets import PropertyWidget, PresetComboActionType
from tb_lattice_viewer.widgets import VectorWidget


class ScalarPropertyWidget(PropertyWidget):
    actionSelectedSignal = pyqtSignal(PresetComboActionType)

    def __init__(
            self,
            name: str = "",
            value: str = "",
            category="scalar-property",
            *args,
            **kwargs,
    ):
        super().__init__(presetName=category, *args, **kwargs)
        self.buildUI()
        self.setConfig(dict(name=name, value=value))
        self.setContentsMargins(1, 1, 1, 1)

    @property
    def name(self) -> str:
        return self.nameEdit.text().strip()

    @property
    def value(self) -> Any:
        return self.valueEdit.text().strip()

    def buildUI(self):
        self.nameEdit = QLineEdit()
        self.valueEdit = QLineEdit()

        presetLayout = self.buildPresetsControlsCombo(self.itemAction)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.nameEdit)
        mainLayout.addWidget(QLabel("="))
        mainLayout.addWidget(self.valueEdit)
        mainLayout.addWidget(presetLayout)
        self.setLayout(mainLayout)

    @property
    def currentPreset(self) -> Optional[str]:
        return self.nameEdit.text()

    def itemAction(self, action: PresetComboActionType):
        print("Action:", action)
        if action == PresetComboActionType.SAVE_AS_PRESET:
            self.addPreset(self.currentPreset)
        elif action == PresetComboActionType.GET_FROM_PRESET:
            preset = self.selectPreset()
            self.setConfigFromPreset(preset)

        self.actionSelectedSignal.emit(action)

    def isEmpty(self):
        if self.name == "" and self.value == "":
            return True
        return False

    def isValid(self):
        if self.name != "" and self.value != "":
            return True
        return False

    def toFortranDefinition(self) -> Optional[str]:

        value = eval(self.value)
        name = self.name

        type2fType = {
            int: "integer",
            float: "double precision",
            bool: "logical",
            complex: "complex*16",
        }
        fType = type2fType[type(value)].upper()
        if isinstance(value, complex):
            value = f"CMPLX({value.real, value.imag})"

        return f"{fType}, PARAMETER :: {name} = {value}"

    def setConfig(self, config):
        self.nameEdit.setText(config.get("name", "unknown"))
        self.valueEdit.setText(config.get("value", "0"))

    def getConfig(self):
        return {"name": self.nameEdit.text(), "value": self.valueEdit.text()}


class SitePropertyWidget(PropertyWidget):
    actionSelectedSignal = pyqtSignal(PresetComboActionType)

    def __init__(
            self,
            name: str = "",
            value=(0, 0, 0),
            size=1,
            color=QColor("white"),
            *args,
            **kwargs,
    ):
        super().__init__(presetName="vector-property", *args, **kwargs)
        self.buildUI()
        self.setConfig(dict(name=name, value=value, size=size, color=color))
        self.setContentsMargins(1, 1, 1, 1)

    def buildUI(self):
        self.valueWidget = VectorWidget("x")
        self.sizeSpinBox = QDoubleSpinBox()
        self.sizeSpinBox.setValue(1)
        self.sizeSpinBox.setMaximum(10e5)
        self.sizeSpinBox.setDecimals(4)
        self.sizeSpinBox.setSingleStep(0.01)
        self.sizeSpinBox.setMaximumWidth(100)

        self.siteColorLabel = QPushButton("Color")
        sizeLabel = QLabel("<b>d=</b>")
        sizeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        presetLayout = self.buildPresetsControlsCombo(self.itemAction, savable=False)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.valueWidget)
        mainLayout.addWidget(sizeLabel)
        mainLayout.addWidget(self.sizeSpinBox)
        mainLayout.addWidget(self.siteColorLabel)
        mainLayout.addWidget(presetLayout)
        self.setLayout(mainLayout)

        self.siteColorLabel.clicked.connect(self.siteColorPicker)

    @property
    def size(self) -> float:
        return self.sizeSpinBox.value()

    @property
    def position(self) -> QVector3D:
        return self.valueWidget.vec()

    @property
    def color(self) -> QColor:
        return QColor(*self.siteColorLabel.color)

    def itemAction(self, action: PresetComboActionType):
        self.actionSelectedSignal.emit(action)

    @property
    def currentPreset(self) -> Optional[str]:
        return self.valueWidget.name

    def siteColorPicker(self):
        color = QColorDialog.getColor()
        color = (color.red(), color.green(), color.blue())
        self.siteColorLabel.setStyleSheet(f"QWidget {{ background-color: rgb{color}}}")
        self.siteColorLabel.color = color

    def setConfig(self, config):

        self.valueWidget.setName(config.get("name", "unknown"))
        self.valueWidget.setValue(config.get("value", (0, 0)))
        self.sizeSpinBox.setValue(config.get("size", 1.0))
        color = config.get("color", (255, 255, 255))

        if isinstance(color, QColor):
            color = (color.red(), color.green(), color.blue())

        elif isinstance(color, list):
            color = tuple(color)

        self.siteColorLabel.color = color
        self.siteColorLabel.setStyleSheet(f"QWidget {{ background-color: rgb{color}}}")

    def getConfig(self):
        return {
            "name": self.valueWidget.name,
            "value": self.valueWidget.getValue(),
            "size": self.sizeSpinBox.value(),
            "color": self.siteColorLabel.color,
        }


class ScalarPropertiesListWidget(PropertyWidget):
    def __init__(self, preset: str = None, *args, **kwargs):
        super().__init__("scalar-property-list", *args, **kwargs)
        self.scalarsList = QListWidget()
        self.scalarsList.setMinimumHeight(200)
        self.addScalar()
        self.buildUI()
        self.updatePresets(preset)
        self.setContentsMargins(1, 1, 1, 1)

    def buildUI(self):
        presetLayout = self.buildPresetLayout()
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(presetLayout)
        mainLayout.addWidget(self.scalarsList)
        self.setLayout(mainLayout)

    @property
    def currentPreset(self) -> str:
        return self.presetsCombo.currentText()

    def addScalar(self, name: str = "", value: str = ""):
        item = QListWidgetItem("")
        widget = ScalarPropertyWidget(name, value)
        item.setSizeHint(widget.sizeHint())
        self.scalarsList.addItem(item)
        self.scalarsList.setItemWidget(item, widget)

        def callback(action: PresetComboActionType):
            self.itemActionTriggered(item, widget, action)

        widget.actionSelectedSignal.connect(callback)

    def itemActionTriggered(
            self,
            item: QListWidgetItem,
            widget: ScalarPropertyWidget,
            action: PresetComboActionType,
    ):
        if action == PresetComboActionType.ADD_NEW_ITEM:
            self.addScalar()
        elif action == PresetComboActionType.DELETE_ITEM:
            if self.scalarsList.count() > 1:
                print(self.scalarsList.takeItem(self.scalarsList.row(item)))


    def setConfig(self, config):
        self.scalarsList.clear()
        if isinstance(config, list):
            for param in config:
                self.addScalar(**param)

    def getConfig(self):
        params = []
        for i in range(self.scalarsList.count()):
            item = self.scalarsList.item(i)
            widget: ScalarPropertyWidget = self.scalarsList.itemWidget(item)
            params.append(widget.getConfig())
        return params

    def properties(self) -> List[ScalarPropertyWidget]:
        widgets = []
        for i in range(self.scalarsList.count()):
            item = self.scalarsList.item(i)
            widget: ScalarPropertyWidget = self.scalarsList.itemWidget(item)
            widgets.append(widget)
        return widgets


class LatticeDefinitionWidget(PropertyWidget):
    def __init__(self, preset: str = None, *args, **kwargs):
        super().__init__("lattice-definition", *args, **kwargs)
        self.v1 = VectorWidget("v1")
        self.v2 = VectorWidget("v2")
        self.unitCellDefinition = LatticeUnitCellDefinitionWidget()
        self.buildUI()
        self.updatePresets(preset)
        self.setContentsMargins(1, 1, 1, 1)

    def buildUI(self):
        presetLayout = self.buildPresetLayout()
        mainLayout = QVBoxLayout()

        mainLayout.addLayout(presetLayout)
        mainLayout.addWidget(self.v1)
        mainLayout.addWidget(self.v2)
        mainLayout.addWidget(self.unitCellDefinition)

        self.setLayout(mainLayout)

    @property
    def currentPreset(self) -> str:
        return self.presetsCombo.currentText()

    def getLatticePosition(self, i, j) -> QVector3D:
        return i * self.v1.vec() + j * self.v2.vec()

    def setConfig(self, config):
        self.v1.setValue(config.get("v1", (0, 1)))
        self.v2.setValue(config.get("v2", (1, 0)))
        self.unitCellDefinition.setConfig(config.get("sites"))

    def getConfig(self):
        return {
            "v1": self.v1.getValue(),
            "v2": self.v2.getValue(),
            "sites": self.unitCellDefinition.getConfig(),
        }

    def toFortranDefinition(self) -> str:
        prefix = "double precision, dimension(2), parameter :: "
        latticeStr = f"{prefix} unit_cell_v1 = {self.v1.toFortranListStr()}\n" \
                     f"{prefix} unit_cell_v2 = {self.v2.toFortranListStr()}\n"

        vectorsStr = self.unitCellDefinition.toFortranListStr()

        numUnits = self.unitCellDefinition.numUnits
        vectorsStr = f"double precision, dimension({numUnits}, 2), parameter :: unit_cell_positions = {vectorsStr}"

        return f"\n{latticeStr}\n{vectorsStr}\n".upper()


class LatticeUnitCellDefinitionWidget(PropertyWidget):
    def __init__(self, preset: str = None, *args, **kwargs):
        super().__init__("lattice-unit-cell-definition", *args, **kwargs)
        self.sitesList = QListWidget()
        self.sitesList.setMinimumHeight(100)
        self.addSite("v", (0, 0))
        self.buildUI()

    def buildUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sitesList)
        self.setLayout(mainLayout)

    @property
    def currentPreset(self) -> str:
        return self.presetsCombo.currentText()

    def unitCellSites(self) -> List[SitePropertyWidget]:
        widgets = []
        for i in range(self.sitesList.count()):
            item = self.sitesList.item(i)
            widget: SitePropertyWidget = self.sitesList.itemWidget(item)
            widgets.append(widget)
        return widgets

    @property
    def numUnits(self) -> int:
        return len(self.unitCellSites())

    def toFortranListStr(self) -> str:
        definition = []
        for widget in self.unitCellSites():
            values = widget.valueWidget.getValue()
            definition += [f"{v}" for v in values]

        definition = ", ".join(definition)
        definition = f"reshape((/{definition}/), (/{self.numUnits}, 2/))"
        return definition

    def addSite(self, name: str, value, size=1, color=QColor("white")):
        item = QListWidgetItem("")
        widget = SitePropertyWidget(name, value, size, color)

        item.setSizeHint(widget.sizeHint())

        self.sitesList.addItem(item)
        self.sitesList.setItemWidget(item, widget)

        def callback(action: PresetComboActionType):
            self.itemActionTriggered(item, widget, action)

        widget.actionSelectedSignal.connect(callback)

    def itemActionTriggered(
            self,
            item: QListWidgetItem,
            widget: SitePropertyWidget,
            action: PresetComboActionType,
    ):
        if action == PresetComboActionType.ADD_NEW_ITEM:
            self.addSite("v", (0, 0))
        elif action == PresetComboActionType.DELETE_ITEM:
            if self.sitesList.count() > 1:
                self.sitesList.takeItem(self.sitesList.row(item))

    def setConfig(self, config):
        self.sitesList.clear()
        if config is None:
            self.addSite("v", (0, 0))
        elif isinstance(config, list):
            for param in config:
                self.addSite(**param)

    def getConfig(self):
        params = []
        for i in range(self.sitesList.count()):
            item = self.sitesList.item(i)
            widget: SitePropertyWidget = self.sitesList.itemWidget(item)
            params.append(widget.getConfig())
        return params
