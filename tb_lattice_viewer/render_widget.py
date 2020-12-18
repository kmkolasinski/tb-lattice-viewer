from PyQt5 import QtCore
from PyQt5.Qt3DCore import *
from PyQt5.Qt3DExtras import *
from PyQt5.Qt3DRender import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class RenderWidget(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.view = Qt3DWindow()

		self.widget = QWidget.createWindowContainer(self.view, self)
		self.scene = QEntity()

		# self.picker = QObjectPicker(self.scene)
		# self.picker.setHoverEnabled(True)
		# self.picker.setDragEnabled(True)
		# self.scene.addComponent(self.picker)

		# camera
		self.camera: QCamera = self.view.camera()
		self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000)
		self.camera.setPosition(QVector3D(0, 0, 1))
		self.camera.setNearPlane(0.01)
		self.camera.setViewCenter(QVector3D(0, 0, 0))

		# for camera control
		camController = QFirstPersonCameraController(self.scene)
		camController.setCamera(self.camera)
		self.view.setRootEntity(self.scene)
		layout = QVBoxLayout()
		layout.addWidget(self.widget)
		self.setLayout(layout)

		renderSettings: QRenderSettings = self.view.renderSettings()
		renderCapabilities: QRenderCapabilities = renderSettings.renderCapabilities()
		print("renderSettings            :", renderSettings.activeFrameGraph())
		print("renderPolicy			     :", renderSettings.renderPolicy())
		print("renderCapabilities.profile:", renderCapabilities.profile())

		# picking_settings: QPickingSettings = render_settings.pickingSettings()
		# picking_settings.setFaceOrientationPickingMode(QPickingSettings.FrontFace)
		# picking_settings.setPickMethod(QPickingSettings.BoundingVolumePicking)
		# picking_settings.setPickResultMode(QPickingSettings.NearestPick)

		# self.picker.pressed.connect(self.clicked)
		# self.picker.clicked.connect(self.clicked)
		# self.picker.moved.connect(self.clicked)

	def setScene(self, sceneFn):
		c = self.scene.children()
		for e in c:
			e.deleteLater()

		sceneFn(self.scene)
		camController = QOrbitCameraController(self.scene)
		camController.setLinearSpeed(2.0)
		camController.setLookSpeed(2.0)
		camController.setZoomInLimit(0.25)

		camController.setAcceleration(5)
		camController.setDeceleration(10)
		camController.setCamera(self.camera)

	def sizeHint(self) -> QtCore.QSize:
		return QSize(800, 600)

	def clicked(self, event: QPickEvent, *args, **kwargs):
		print("clicked - not implemented", event.objectName())