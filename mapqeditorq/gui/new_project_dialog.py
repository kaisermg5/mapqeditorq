
from .new_project_dialog_ui import Ui_NewProjectDialog
from ..mqeq_logic import common


from PyQt5 import QtGui, QtWidgets
import os


class NewProjectDialog(QtWidgets.QDialog):
    def __init__(self, handler):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_NewProjectDialog()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(common.EDITOR_DIRECTORY, 'resources/mqeq-icon.ico'))
                       , QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.ui.setupUi(self)
        self.handler = handler

        self.ui.btn_browse_dir.clicked.connect(self.browse_dir)
        self.ui.btn_browse_rom.clicked.connect(self.browse_rom)
        self.ui.btn_create.clicked.connect(self.create_project_clicked)

    def error_msg(self, description):
        QtWidgets.QMessageBox.critical(self, 'Error', description, QtWidgets.QMessageBox.Ok)

    def browse_dir(self):
        dir_name = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select the project's directory"
        )
        if dir_name:
            self.ui.txt_proj_dir.setText(dir_name)

    def browse_rom(self):
        rom_filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select base ROM file',
            self.handler.settings.last_opened_path,
            'GBA ROM (*.gba);;All files (*)'
        )

        if rom_filename:
            self.ui.txt_baserom.setText(rom_filename)

    def create_project_clicked(self):
        rom_filename = self.ui.txt_baserom.text().strip()
        dir_name = self.ui.txt_proj_dir.text().strip()
        project_name = self.ui.txt_proj_name.text().strip()
        if not rom_filename:
            self.error_msg('You must specify a BZME rom to use as base for the project.')

        elif not dir_name:
            self.error_msg('You must specify the directory where the project will be created.')
        elif not project_name:
            self.error_msg('You must specify a project name.')
        elif not os.path.isabs(rom_filename) or not os.path.isabs(dir_name):
            self.error_msg("Both the base rom and the project's directory, must be absolute paths")
        else:
            try:
                self.setEnabled(False)

                self.handler.new_project(rom_filename, dir_name, project_name)
                self.close()
            except common.MqeqError as e:
                self.setEnabled(True)
                self.error_msg(str(e))





