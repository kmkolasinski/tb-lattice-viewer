import json
from abc import abstractmethod
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtWidgets import *
from natsort import natsorted

from tb_lattice_viewer.widgets import ParamsListDialog


class PresetsManager:
    savePath: Path = Path("presets.json")
    presets = defaultdict(dict)

    @classmethod
    def getPresets(cls, category: str) -> Dict[str, Any]:
        return cls.presets.get(category, {})

    @classmethod
    def getPreset(cls, category: str, name: str) -> Dict[str, Any]:
        return cls.getPresets(category).get(name, {})

    @classmethod
    def getPresetsNames(cls, category: str) -> List[str]:
        return natsorted(cls.getPresets(category).keys())

    @classmethod
    def deletePreset(cls, category: str, name: str):
        if category in cls.presets:
            if name in cls.presets[category]:
                del cls.presets[category][name]
        cls.save()

    @classmethod
    def updatePreset(cls, category: str, name: str, config: Dict[str, Any]):
        print(f"Updating preset: {category}: {name}")
        if category not in cls.presets:
            cls.presets[category] = {}
        cls.presets[category][name] = deepcopy(config)
        cls.save()

    @classmethod
    def save(cls):
        print(f"Saving presets: {cls.savePath}")
        with open(cls.savePath, "w") as file:
            json.dump(cls.presets, file, indent=2)

    @classmethod
    def load(cls, savePath: Path):
        cls.savePath = savePath
        print(f"Loading presets: {cls.savePath}")
        if not Path(cls.savePath).exists():
            return
        with open(cls.savePath, "r") as file:
            cls.presets = json.load(file)


class PresetComboActionType(Enum):
    ADD_NEW_ITEM = "Add new"
    DELETE_ITEM = "Delete"
    SAVE_AS_PRESET = "Save as preset"
    GET_FROM_PRESET = "Load from preset"


class PropertyWidget(QWidget):
    def __init__(self, presetName: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = presetName
        self.dialog = ParamsListDialog(
            PresetsManager.getPresetsNames(self.category),
            allow_add=False,
            allow_delete=False,
        )

    def buildUI(self):
        presetLayout = self.buildPresetLayout()
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(presetLayout)
        self.setLayout(mainLayout)

    def buildPresetLayout(self):
        self.presetsCombo = QComboBox()
        self.presetNameLabel = QLabel(self.category)
        self.savePresetButton = QPushButton("Save")
        self.deletePresetButton = QPushButton("Del")
        self.addPresetButton = QPushButton("Add")

        self.presetsCombo.currentIndexChanged.connect(self.presetSelected)
        self.savePresetButton.pressed.connect(self.savePreset)
        self.addPresetButton.pressed.connect(self.addPreset)
        self.deletePresetButton.pressed.connect(self.deletePreset)

        presetLayout = QHBoxLayout()
        presetLayout.addWidget(QLabel("Presets"))
        presetLayout.addWidget(self.presetsCombo)
        presetLayout.addWidget(self.savePresetButton)
        presetLayout.addWidget(self.addPresetButton)
        presetLayout.addWidget(self.deletePresetButton)
        return presetLayout

    def buildPresetsControlsCombo(self, callbackFn, savable=True):
        controls = QComboBox()
        controls.setFixedWidth(40)
        controls.addItem("...")
        controls.addItem(PresetComboActionType.ADD_NEW_ITEM.value)
        controls.addItem(PresetComboActionType.DELETE_ITEM.value)
        if savable:
            controls.addItem(PresetComboActionType.SAVE_AS_PRESET.value)
            controls.addItem(PresetComboActionType.GET_FROM_PRESET.value)

        def call():
            current = controls.currentText()
            if current == "...":
                return
            try:
                action = PresetComboActionType(current)
                callbackFn(action)
            except Exception as e:
                title = f"Cannot perform action {current}"
                QMessageBox.critical(self, "Error", "<p><b>%s</b></p>%s" % (title, e))
            controls.setCurrentIndex(0)

        controls.currentIndexChanged.connect(call)
        return controls

    def selectPreset(self):
        self.dialog = ParamsListDialog(
            PresetsManager.getPresetsNames(self.category),
            allow_add=False,
            allow_delete=False,
        )
        if self.currentPreset is not None:
            self.dialog.selectItem(self.currentPreset)

        self.dialog.exec()
        selectedPreset = self.dialog.selectedItem()
        return selectedPreset

    def setConfigFromPreset(self, name: str):
        config = PresetsManager.getPreset(self.category, name)
        self.setConfig(config)

    @property
    def currentPreset(self) -> Optional[str]:
        return None

    def presetSelected(self, *args):
        if self.currentPreset is not None:
            preset = PresetsManager.getPreset(self.category, self.currentPreset)
            self.setConfig(preset)

    def savePreset(self):
        PresetsManager.updatePreset(self.category, self.currentPreset, self.getConfig())

    def addPreset(self, default: str = "name"):
        name, ok = QInputDialog.getText(
            self, "Add new preset", "Enter name:", text=default
        )
        if ok:
            PresetsManager.updatePreset(self.category, name, self.getConfig())
            self.updatePresets(name)

    def deletePreset(self):
        PresetsManager.deletePreset(self.category, self.currentPreset)
        self.updatePresets()

    def updatePresets(self, name: str = None):
        self.presetsCombo.clear()
        self.presetsCombo.addItems(PresetsManager.getPresetsNames(self.category))
        if name is not None:
            self.presetsCombo.setCurrentText(name)

    @abstractmethod
    def getConfig(self):
        return {}

    @abstractmethod
    def setConfig(self, config):
        pass
