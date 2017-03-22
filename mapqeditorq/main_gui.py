# -*- coding: utf-8 -*-

import os
import sys
import pickle

from PIL import Image, ImageQt

from .editor_ui import Ui_MainWindow
from PyQt5 import QtWidgets

EDITOR_DIRECTORY = os.path.dirname(os.path.realpath(sys.argv[0]))
SETTINGS_FILENAME = os.path.join(EDITOR_DIRECTORY, 'settings.dat')


class UserSettings:
    def __init__(self):
        self.last_opened_path = '.'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Setup Window
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Load settings
        if os.path.exists(SETTINGS_FILENAME):
            with open(SETTINGS_FILENAME, 'rb') as f:
                self.settings = pickle.load(f)
            if not isinstance(self.settings, UserSettings):
                self.settings = UserSettings()
        else:
            self.settings = UserSettings()

        pass

    # Closing events
    def closeEvent(self, event):
        if self.close_rom_confirm():
            event.ignore()
            return
        self.save_settings()
        event.accept()

    def close_rom_confirm(self):
        pass

    def save_settings(self):
        pass

    # Menu Options
    def open_rom(self, filename=None):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    r = app.exec_()
    app.deleteLater()
    sys.exit(r)

if __name__ == '__main__':
    main()
