# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_project_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewProjectDialog(object):
    def setupUi(self, NewProjectDialog):
        NewProjectDialog.setObjectName("NewProjectDialog")
        NewProjectDialog.resize(400, 285)
        self.gridLayout = QtWidgets.QGridLayout(NewProjectDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_create = QtWidgets.QPushButton(NewProjectDialog)
        self.btn_create.setObjectName("btn_create")
        self.gridLayout.addWidget(self.btn_create, 5, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(NewProjectDialog)
        font = QtGui.QFont()
        font.setKerning(True)
        self.groupBox.setFont(font)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.btn_browse_dir = QtWidgets.QPushButton(self.groupBox)
        self.btn_browse_dir.setObjectName("btn_browse_dir")
        self.gridLayout_2.addWidget(self.btn_browse_dir, 2, 2, 1, 1)
        self.btn_browse_rom = QtWidgets.QPushButton(self.groupBox)
        self.btn_browse_rom.setObjectName("btn_browse_rom")
        self.gridLayout_2.addWidget(self.btn_browse_rom, 4, 2, 1, 1)
        self.txt_proj_dir = QtWidgets.QLineEdit(self.groupBox)
        self.txt_proj_dir.setObjectName("txt_proj_dir")
        self.gridLayout_2.addWidget(self.txt_proj_dir, 1, 1, 1, 2)
        self.txt_proj_name = QtWidgets.QLineEdit(self.groupBox)
        self.txt_proj_name.setObjectName("txt_proj_name")
        self.gridLayout_2.addWidget(self.txt_proj_name, 0, 1, 1, 2)
        self.txt_baserom = QtWidgets.QLineEdit(self.groupBox)
        self.txt_baserom.setObjectName("txt_baserom")
        self.gridLayout_2.addWidget(self.txt_baserom, 3, 1, 1, 2)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.retranslateUi(NewProjectDialog)
        QtCore.QMetaObject.connectSlotsByName(NewProjectDialog)

    def retranslateUi(self, NewProjectDialog):
        _translate = QtCore.QCoreApplication.translate
        NewProjectDialog.setWindowTitle(_translate("NewProjectDialog", "Dialog"))
        self.btn_create.setText(_translate("NewProjectDialog", "Create Project"))
        self.groupBox.setTitle(_translate("NewProjectDialog", "Project"))
        self.label.setText(_translate("NewProjectDialog", "Name:"))
        self.label_2.setText(_translate("NewProjectDialog", "Directory:"))
        self.btn_browse_dir.setText(_translate("NewProjectDialog", "Browse Directory"))
        self.btn_browse_rom.setText(_translate("NewProjectDialog", "Browse ROM"))
        self.label_3.setText(_translate("NewProjectDialog", "BZME base rom:"))

