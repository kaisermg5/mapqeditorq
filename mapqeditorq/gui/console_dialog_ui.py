# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'console_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConsoleDialog(object):
    def setupUi(self, ConsoleDialog):
        ConsoleDialog.setObjectName("ConsoleDialog")
        ConsoleDialog.resize(718, 300)
        self.gridLayout = QtWidgets.QGridLayout(ConsoleDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.txt_console = QtWidgets.QTextEdit(ConsoleDialog)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 235, 231))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.txt_console.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MUTT ClearlyU Wide")
        self.txt_console.setFont(font)
        self.txt_console.setUndoRedoEnabled(False)
        self.txt_console.setReadOnly(True)
        self.txt_console.setObjectName("txt_console")
        self.gridLayout.addWidget(self.txt_console, 0, 0, 1, 1)
        self.btn_close = QtWidgets.QPushButton(ConsoleDialog)
        self.btn_close.setObjectName("btn_close")
        self.gridLayout.addWidget(self.btn_close, 1, 0, 1, 1)

        self.retranslateUi(ConsoleDialog)
        QtCore.QMetaObject.connectSlotsByName(ConsoleDialog)

    def retranslateUi(self, ConsoleDialog):
        _translate = QtCore.QCoreApplication.translate
        ConsoleDialog.setWindowTitle(_translate("ConsoleDialog", "Console output"))
        self.btn_close.setText(_translate("ConsoleDialog", "Close"))

