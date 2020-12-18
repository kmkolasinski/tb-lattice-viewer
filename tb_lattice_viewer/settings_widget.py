import glob
import importlib
import os
import traceback
import uuid
from typing import Optional

import numpy
from PyQt5 import QtCore
from PyQt5.Qt3DCore import *
from PyQt5.Qt3DExtras import *
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QVector3D, QColor
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QMessageBox
from numpy import f2py
from tqdm import tqdm

from tb_lattice_viewer.editor import createCodeEditor
from tb_lattice_viewer.presets import PropertyWidget
from tb_lattice_viewer.property_widgets import (
    ScalarPropertiesListWidget,
    LatticeDefinitionWidget,
)
from tb_lattice_viewer.templates import (
    FORTRAN_CODE_MASK_FN_TEMPLATE,
    FORTRAN_CODE_MODULE_TEMPLATE,
)
from tb_lattice_viewer.widgets import VectorWidget, CollapsibleBox


class SettingsWidget(PropertyWidget):
    def getConfig(self):
        return {
            "parameters": self.properties.getConfig(),
            "lattice": self.lattice.getConfig(),
            "code": self.editor.text(),
            "dimensions": {"vMin": self.vMin.getValue(), "vMax": self.vMax.getValue()},
        }

    def setConfig(self, config):
        print("main:config:", config)
        self.properties.setConfig(config.get("parameters", {}))
        self.lattice.setConfig(config.get("lattice", {}))
        self.editor.setText(config.get("code", FORTRAN_CODE_MASK_FN_TEMPLATE))
        self.vMin.setValue(config.get("dimensions", {"vMin": (0, 0)})["vMin"])
        self.vMax.setValue(config.get("dimensions", {"vMax": (1, 1)})["vMax"])

    def __init__(self, *args, **kwargs):
        super().__init__(presetName="lattice", *args, **kwargs)

        self.compileButton = QPushButton("Compile and generate lattice")
        self.properties = ScalarPropertiesListWidget()
        self.lattice = LatticeDefinitionWidget()
        self.vMin = VectorWidget("Minimum (x, y)")
        self.vMax = VectorWidget("Maximum (x, y)")

        t1 = CollapsibleBox(title="Constants")
        t1.setContentLayout(self.properties.layout())

        t2 = CollapsibleBox(title="Lattice")
        t2.setContentLayout(self.lattice.layout())

        t3 = CollapsibleBox(title="Dimensions")

        dimLayout = QVBoxLayout()
        dimLayout.addWidget(self.vMin)
        dimLayout.addWidget(self.vMax)

        t3.setContentLayout(dimLayout)

        self.editor = createCodeEditor(FORTRAN_CODE_MASK_FN_TEMPLATE)

        mainLayout = QVBoxLayout()
        presetsBar = self.buildPresetLayout()
        mainLayout.addLayout(presetsBar)
        mainLayout.addWidget(t1)
        mainLayout.addWidget(t2)
        mainLayout.addWidget(t3)

        mainLayout.addWidget(QLabel("<b>Editor</b>"))
        mainLayout.addWidget(self.editor)
        mainLayout.addWidget(self.compileButton)
        self.setLayout(mainLayout)
        self.updatePresets()

        self.entities = []

    def sizeHint(self) -> QtCore.QSize:
        return QSize(300, 800)

    @property
    def currentPreset(self) -> str:
        return self.presetsCombo.currentText()

    def getLatticeStartEndIndices(self):
        xyMin = self.vMin.asTuple()
        xyMax = self.vMax.asTuple()
        s1x1, s1y1 = self.lattice.v1.getStepIndexAt(*xyMin)
        s1x2, s1y2 = self.lattice.v1.getStepIndexAt(*xyMax)
        s2x1, s2y1 = self.lattice.v2.getStepIndexAt(*xyMin)
        s2x2, s2y2 = self.lattice.v2.getStepIndexAt(*xyMax)
        x = s1x1, s1x2, s2x1, s2x2
        y = s1y1, s1y2, s2y1, s2y2
        return min(x), min(y), max(x), max(y)

    def isInWindow(self, vec: QVector3D) -> bool:
        xMin, yMin = self.vMin.asTuple()
        xMax, yMax = self.vMax.asTuple()
        if vec.x() < xMin or vec.x() > xMax:
            return False
        if vec.y() < yMin or vec.y() > yMax:
            return False
        return True

    def buildSourceCode(self) -> Optional[str]:
        source = FORTRAN_CODE_MODULE_TEMPLATE
        try:
            params = []
            for k, prop in enumerate(self.properties.properties()):
                if prop.isEmpty():
                    continue
                if not prop.isValid():
                    title = f"Missing name or value for property {k+1}"
                    error = f"Set correct name or value"
                    QMessageBox.critical(
                        self, "Invalid property", "<p><b>%s</b></p>%s" % (title, error)
                    )
                    return None
                paramStr = prop.toFortranDefinition()
                params.append(paramStr)

            params = "\n".join(params)

            params = f"\n{params}\n{self.lattice.toFortranDefinition()}\n"

            source = source.replace("{{PARAMETERS}}", params)
            source = source.replace("{{MODULE_NAME}}", self.currentPreset)
            source = source.replace("{{FUNCTIONS}}", self.editor.text())

        except Exception as error:
            title = f"Cannot parse source code"
            traceback.print_exc()
            QMessageBox.critical(self, "Error", "<p><b>%s</b></p>%s" % (title, error))
            return None

        return source

    def compileSourceCode(self):
        source = self.buildSourceCode()
        if source is None:
            return None

        if self.currentPreset in ["", None]:
            title = f"No preset defined. Create new preset by clicking add!"
            QMessageBox.critical(self, "No preset", f"<p>{title}</p>")
            return None

        print(">> SOURCE")
        print(source)
        modulename = f"module_{uuid.uuid4().hex}"

        result = f2py.compile(
            source,
            modulename=modulename,
            verbose=True,
            extension=".f90",
            source_fn=f"mod_{self.currentPreset}.f90",
        )
        if result != 0:
            title = f"Cannot compile Fortran code! Check console for output!"
            raise ValueError(title)

        m = importlib.import_module(modulename)

        def maskFn(x, y, z=0):
            mask = getattr(m, self.currentPreset).mask(float(x), float(y), float(z))
            return mask

        for p in glob.glob(f"{modulename}*.so"):
            os.remove(p)

        self.maskFunction = maskFn
        return True

    def createScene(self, rootEntity: QEntity):

        sXmin, sYmin, sXmax, sYmax = self.getLatticeStartEndIndices()
        print("sXmin, sYmin, sXmax, sYmax :", sXmin, sYmin, sXmax, sYmax)
        sites = self.lattice.unitCellDefinition.unitCellSites()
        maskFn = self.maskFunction

        positions = []
        for i in range(sXmin, sXmax + 1):
            for j in range(sYmin, sYmax + 1):
                position = self.lattice.getLatticePosition(i, j)
                if not self.isInWindow(position):
                    continue
                for site in sites:
                    pos = position + site.position
                    if maskFn(pos.x(), pos.y(), pos.z()) == 0:
                        continue

                    positions.append([pos.x(), pos.y(), pos.z()])

        positions = numpy.array(positions)
        maxPos = positions.max(0)
        minPos = positions.min(0)
        norm = 1 / max(numpy.linalg.norm(maxPos - minPos), 1)
        minPos = QVector3D(*minPos.tolist())

        site2mesh = {}
        for site in sites:
            sphereMesh = QSphereMesh()
            sphereMesh.setRadius(site.size * norm)
            sphereMesh.setRings(10)
            sphereMesh.setSlices(10)
            material = QGoochMaterial(rootEntity)
            material.setWarm(site.color)
            material.setCool(QColor("white"))
            site2mesh[site] = {"mesh": sphereMesh, "material": material}

        index = 0
        for i in tqdm(range(sXmin, sXmax + 1)):
            for j in range(sYmin, sYmax + 1):
                position = self.lattice.getLatticePosition(i, j)
                if not self.isInWindow(position):
                    continue

                for site in sites:

                    pos = position + site.position

                    if maskFn(pos.x(), pos.y(), pos.z()) == 0:
                        continue

                    # sphereEntity = QEntity(rootEntity)

                    # sphereMesh = QSphereMesh()
                    # sphereMesh.setRadius(site.size * norm)
                    # sphereMesh.setRings(10)
                    # sphereMesh.setSlices(10)
                    # material = QGoochMaterial(rootEntity)
                    # material.setWarm(site.color)
                    # material.setCool(QColor("white"))
                    # sphereTransform = QTransform()
                    # sphereEntity.addComponent(sphereTransform)
                    # sphereEntity.addComponent(material)
                    # sphereEntity.addComponent(sphereMesh)

                    # if index >= len(self.entities):
                    #     sphereEntity = QEntity(rootEntity)
                    #
                    #     sphereMesh = QSphereMesh()
                    #     sphereMesh.setRadius(site.size * norm)
                    #     sphereMesh.setRings(10)
                    #     sphereMesh.setSlices(10)
                    #     material = QGoochMaterial(rootEntity)
                    #     material.setWarm(site.color)
                    #     material.setCool(QColor("white"))
                    #     sphereTransform = QTransform()
                    #     sphereEntity.addComponent(sphereTransform)
                    #     sphereEntity.addComponent(material)
                    #     sphereEntity.addComponent(sphereMesh)
                    #
                    #     self.entities.append(sphereEntity)
                    # else:
                    #     sphereEntity = self.entities[index]
                    #
                    sphereEntity = QEntity(rootEntity)
                    pos = (pos - minPos) * norm

                    sphereTransform = QTransform()
                    sphereTransform.setTranslation(pos)

                    sphereEntity.addComponent(sphereTransform)
                    sphereEntity.addComponent(site2mesh[site]["mesh"])
                    sphereEntity.addComponent(site2mesh[site]["material"])

        return rootEntity
