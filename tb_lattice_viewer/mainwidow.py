import traceback

from PyQt5.QtWidgets import *

from tb_lattice_viewer.render_widget import RenderWidget
from tb_lattice_viewer.settings_widget import SettingsWidget


class App(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.settingsWidget = SettingsWidget()
		self.renderWidget = RenderWidget()

		scroll = QScrollArea()
		scroll.setMaximumWidth(600)
		scroll.setWidget(self.settingsWidget)
		scroll.setWidgetResizable(True)

		h = QHBoxLayout()
		h.addWidget(scroll)
		h.addWidget(self.renderWidget)
		self.setLayout(h)

		self.settingsWidget.compileButton.pressed.connect(self.generateScene)

	def generateScene(self):
		try:
			result = self.settingsWidget.compileSourceCode()
			if result is None:
				return
			self.renderWidget.setScene(self.settingsWidget.createScene)
		except Exception as e:
			title = f"Cannot parse"
			traceback.print_exc()
			QMessageBox.critical(self, "Error", "<p><b>%s</b></p>%s" % (title, e))

