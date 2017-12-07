

from .console_dialog_ui import Ui_ConsoleDialog
from ..mqeq_logic import common

from PyQt5 import QtGui, QtWidgets, QtCore
import os


class ConsoleDialog(QtWidgets.QDialog):
    def __init__(self, subprocess_reader):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_ConsoleDialog()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(common.EDITOR_DIRECTORY, 'resources/mqeq-icon.ico'))
                       , QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.ui.setupUi(self)

        self.subprocess_reader = subprocess_reader

        self.ui.btn_close.clicked.connect(self.close)
        self.qthread__ = ConsoleUpadter(self.subprocess_reader)
        self.qthread__.new_line_signal.connect(self.update_console)
        self.qthread__.start()
        self.console_txt = ''

    def update_console(self, newline):
        self.console_txt += newline
        self.ui.txt_console.setText(
            self.console_txt
        )
        self.ui.txt_console.moveCursor(QtGui.QTextCursor.End)


class ConsoleUpadter(QtCore.QThread):
    new_line_signal = QtCore.pyqtSignal(str)

    def __init__(self, subprocess_reader):
        super().__init__()
        self.subprocess_reader = subprocess_reader

    def run(self):
        for line in self.subprocess_reader:
            self.new_line_signal.emit(line)




