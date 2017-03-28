# -*- coding: utf-8 -*-

import os
import sys
import pickle
import time

from PIL import Image, ImageQt

from . import qmapview
from .editor_ui import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui

from .game_utils import Game
from .map_utils import Map


EDITOR_DIRECTORY = os.path.dirname(os.path.realpath(sys.argv[0]))
SETTINGS_FILENAME = os.path.join(EDITOR_DIRECTORY, 'settings.dat')


class UserSettings:
    def __init__(self):
        self.last_opened_path = '.'


def get_tile_num(event, pixmap, tile_size=16):
    pos = event.pos()
    x = int(pos.x())
    y = int(pos.y())
    w = pixmap.width()

    tiles_wide = w // tile_size
    tile_x = x // tile_size
    tile_y = y // tile_size
    tile_num = tile_x + tile_y * tiles_wide
    return tile_num


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Setup Window
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Define main attributes
        self.game = Game()
        self.loaded_map = None

        # Load settings
        if os.path.exists(SETTINGS_FILENAME):
            with open(SETTINGS_FILENAME, 'rb') as f:
                self.settings = pickle.load(f)
            if not isinstance(self.settings, UserSettings):
                self.settings = UserSettings()
        else:
            self.settings = UserSettings()

        # Connect menubar actions
        self.ui.actionOpen_ROM.triggered.connect(lambda: self.open_rom())

        # Connect main widgets
        self.ui.loadmap_button.clicked.connect(self.load_map)
        self.ui.layer1_button.clicked.connect(lambda: self.select_layer(0))
        self.ui.layer2_button.clicked.connect(lambda: self.select_layer(1))

        # Setup Map Layers tab
        self.selected_block = 0
        self.selected_layer = None
        self.map_layer_imgs_qt = None
        self.map_layer_pixmaps = None
        self.map_layer_pixmap_qobjects = None

        self.ui.map_layer_scene = QtWidgets.QGraphicsScene()
        self.ui.map_layer_view.setScene(self.ui.map_layer_scene)


        # Temp things...
        self.ui.blockpart_spinBox.valueChanged.connect(self.show_block_data)

    # Closing events
    def closeEvent(self, event):
        if self.close_rom_confirm():
            event.ignore()
            return

        self.game.close()
        self.save_settings()
        event.accept()

    def close_rom_confirm(self):
        pass

    def save_settings(self):
        with open(SETTINGS_FILENAME, 'wb') as f:
            pickle.dump(self.settings, f)

    # Menu options
    def open_rom(self, filename=None):
        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open ROM file',
                                                                self.settings.last_opened_path,
                                                                'GBA ROM (*.gba);;All files (*)')
        if filename:
            self.settings.last_opened_path = os.path.dirname(filename)

            self.ui.statusbar.showMessage('Loading Rom...')
            if self.game.load(filename):
                # Warning game code doesn't match
                pass
            self.ui.statusbar.showMessage('Rom loaded')
            self.ui.centralwidget.setEnabled(True)

    # Load map
    def load_map(self):
        try:
            map_index = int(self.ui.map_index_ledit.text(), base=16)
            map_subindex = int(self.ui.map_subindex_ledit.text(), base=16)
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Error loading map',
                                           'Both map index and sub index must be hexadecimal numbers')
            return
        self.loaded_map = Map()
        self.ui.statusbar.showMessage('Loading Map...')
        t = time.time()
        try:
            self.loaded_map.load(map_index, map_subindex, self.game)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error loading map', str(e))
            self.ui.statusbar.showMessage('Failed to load the map')
            return
        self.ui.statusbar.showMessage(
            'Map loaded in {} seconds'.format(time.time() - t)
        )

        self.map_layer_imgs_qt = [None, None]
        self.map_layer_pixmaps = [None, None]
        self.map_layer_pixmap_qobjects = [None, None]

        if self.selected_layer is None:
            self.select_layer(0)
            self.select_block(0)
        else:
            self.print_map()

    def print_map(self, quick=False, delete_old=True):
        if not quick or self.map_layer_imgs_qt[self.selected_layer] is None:
            self.map_layer_imgs_qt[self.selected_layer] = ImageQt.ImageQt(
                self.loaded_map.draw_layer(self.selected_layer)
            )

        self.map_layer_pixmaps[self.selected_layer] = QtGui.QPixmap.fromImage(
            self.map_layer_imgs_qt[self.selected_layer]
        )

        if delete_old:
            self.ui.map_layer_scene.clear()
            self.map_layer_pixmap_qobjects[self.selected_layer] = qmapview.QMapPixmap(
                self.map_layer_pixmaps[self.selected_layer]
            )
            self.ui.map_layer_scene.addItem(self.map_layer_pixmap_qobjects[self.selected_layer])

            self.map_layer_pixmap_qobjects[self.selected_layer].clicked.connect(
                self.map_clicked
            )
        else:
            self.map_layer_pixmap_qobjects.set_pixmap(self.map_layer_pixmaps[self.selected_layer])
        self.ui.map_layer_scene.update()

    def select_layer(self, layer_num):
        self.selected_layer = layer_num
        self.print_map(quick=True)

        if layer_num:
            self.ui.layer1_button.setEnabled(True)
            self.ui.layer2_button.setEnabled(False)
        else:
            self.ui.layer1_button.setEnabled(False)
            self.ui.layer2_button.setEnabled(True)

    def select_block(self, block_num):
        self.selected_block = block_num
        self.ui.selectedblock_label.setText(hex(block_num))
        self.show_block_data()

    # Map Layer tab
    def map_clicked(self, event):
        tile_num = get_tile_num(event, self.map_layer_pixmaps[self.selected_layer])
        self.select_block(self.loaded_map.data[self.selected_layer][tile_num])

    def show_block_data(self):
        (tile_num, flip_x, flip_y, palette) = self.loaded_map.get_block_data(
            self.selected_block, self.selected_layer
        )[self.ui.blockpart_spinBox.value()]
        self.ui.tilenum_label.setText(hex(tile_num))
        self.ui.flipx_checkBox.setChecked(flip_x == 1)
        self.ui.flipy_checkBox.setChecked(flip_y == 1)
        self.ui.palettenum_label.setText(hex(palette))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    r = app.exec_()
    app.deleteLater()
    sys.exit(r)

if __name__ == '__main__':
    main()
