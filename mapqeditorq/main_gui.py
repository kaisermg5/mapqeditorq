# -*- coding: utf-8 -*-

import os
import sys
import pickle
import time

from PIL import Image, ImageQt

from . import qmapview
from .editor_ui import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui, QtCore

from .game_utils import Game
from .map_utils import Map


EDITOR_DIRECTORY = os.path.dirname(os.path.realpath(sys.argv[0]))
SETTINGS_FILENAME = os.path.join(EDITOR_DIRECTORY, 'settings.dat')


class UserSettings:
    def __init__(self):
        self.last_opened_path = '.'


def confirm_saving_dialog(title, question='Would you like to save the changes?'):
    msgbox = QtWidgets.QMessageBox()
    msgbox.setWindowTitle(title)
    msgbox.setText(question)
    msgbox.setIcon(QtWidgets.QMessageBox.Question)
    msgbox.setStandardButtons(
        QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel
    )
    msgbox.setDefaultButton(QtWidgets.QMessageBox.Save)
    result = msgbox.exec()
    return result


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


def draw_square_over_tile(pixmap, tile_num, tile_size=16, color=QtCore.Qt.blue):
    tiles_per_line = pixmap.width() // tile_size
    x = (tile_num % tiles_per_line) * tile_size
    y = (tile_num // tiles_per_line) * tile_size

    drawer = QtGui.QPainter(pixmap)
    drawer.setPen(color)
    drawer.drawRect(x, y, tile_size, tile_size)
    drawer.end()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Setup Window
        QtWidgets.QMainWindow.__init__(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(EDITOR_DIRECTORY, 'resources/mqeq-icon.ico'))
                       , QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
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
        self.ui.action_Open_ROM.triggered.connect(lambda: self.open_rom())
        self.ui.action_Save.triggered.connect(lambda: print('save'))

        # Connect main widgets
        self.ui.map_index_ledit.returnPressed.connect(self.load_map)
        self.ui.map_subindex_ledit.returnPressed.connect(self.load_map)
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

        self.layer_blocks_imgs_qt = None
        self.layer_blocks_pixmaps = None
        self.layer_blocks_pixmap_qobjects = None

        self.ui.layer_blocks_scene = QtWidgets.QGraphicsScene()
        self.ui.blocks_view.setScene(self.ui.layer_blocks_scene)

        self.ui.selected_block_ledit.returnPressed.connect(lambda: print('test'))

        # Setup Blocks Editor tab
        self.selected_palette = 0
        self.ui.blocks_view_2.setScene(self.ui.layer_blocks_scene)

        self.tilesets_imgs_qt = None
        self.tileset_pixmaps = None
        self.tileset_pixmap_qobjects = None

        self.ui.tileset_view_scenes = [QtWidgets.QGraphicsScene(),
                                       QtWidgets.QGraphicsScene()]
        self.ui.tileset_view_1.setScene(self.ui.tileset_view_scenes[0])
        self.ui.tileset_view_2.setScene(self.ui.tileset_view_scenes[1])

        self.tile_preview_img_qt = None
        self.tile_preview_pixmap = None
        self.tile_preview_pixmap_qobject = None

        self.ui.tile_preview_scene = QtWidgets.QGraphicsScene()
        self.ui.selected_tile_view.setScene(QtWidgets.QGraphicsScene())

        self.block_preview_img_qt = None
        self.block_preview_pixmap = None
        self.block_preview_pixmap_qobject = None

        self.ui.block_preview_scene = QtWidgets.QGraphicsScene()
        self.ui.selected_block_view.setScene(self.ui.block_preview_scene)

        self.ui.palette_combobox.currentIndexChanged.connect(self.selected_palette_changed)

    # Closing events
    def closeEvent(self, event):
        if not self.close_map_confirm():
            event.ignore()
            return

        self.game.close()
        self.save_settings()
        event.accept()

    def close_map_confirm(self):
        if self.loaded_map is not None and self.loaded_map.was_modified():
            result = confirm_saving_dialog('The map has been modified')
            if result == QtWidgets.QMessageBox.Cancel:
                return False
            elif result == QtWidgets.QMessageBox.Save:
                self.loaded_map.save_to_rom(self.game)
        return True

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

    def save(self):
        pass

    # Load map
    def load_map(self):
        if not self.close_map_confirm():
            return
        try:
            map_index = int(self.ui.map_index_ledit.text(), base=16)
            map_subindex = int(self.ui.map_subindex_ledit.text(), base=16)
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Error loading map',
                                           'Both map index and sub index must be hexadecimal numbers')
            return
        if self.loaded_map is not None and self.loaded_map.get_indexes() == (map_index, map_subindex):
            self.ui.statusbar.showMessage('Map already loaded')
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

        self.layer_blocks_imgs_qt = [None, None]
        self.layer_blocks_pixmaps = [None, None]
        self.layer_blocks_pixmap_qobjects = [None, None]

        self.tilesets_imgs_qt = [None, None]
        self.tileset_pixmaps = [None, None]
        self.tileset_pixmap_qobjects = [None, None]

        if self.selected_layer is None:
            self.select_layer(0)
        else:
            self.print_map()
            self.print_blocks_img()
        self.print_tilesets()

    def select_layer(self, layer_num):
        self.selected_layer = layer_num
        self.print_map(quick=True)
        self.print_blocks_img(quick=True)
        self.print_tilesets()

        if layer_num:
            self.ui.layer1_button.setEnabled(True)
            self.ui.layer2_button.setEnabled(False)
        else:
            self.ui.layer1_button.setEnabled(False)
            self.ui.layer2_button.setEnabled(True)

    def select_block(self, block_num):
        self.selected_block = block_num
        self.print_blocks_img()
        self.ui.selected_block_ledit.setText(hex(block_num))

    def direct_block_selection(self):
        try:
            block_num = int(self.ui.selected_block_ledit.text(), base=16)
        except ValueError:
            block_num = 0
        self.select_block(block_num)

    # Map Layer tab
    def map_clicked(self, event):
        tile_num = get_tile_num(event, self.map_layer_pixmaps[self.selected_layer])
        self.loaded_map.set_map_tile(self.selected_layer, tile_num, self.selected_block)
        self.print_map(delete_old=False)

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
            self.map_layer_pixmap_qobjects[self.selected_layer].set_pixmap(
                self.map_layer_pixmaps[self.selected_layer]
            )
        self.ui.map_layer_scene.update()

    def blocks_img_clicked(self, event):
        block_num = get_tile_num(event, self.layer_blocks_pixmaps[self.selected_layer])
        self.select_block(block_num)

    def print_blocks_img(self, quick=False, delete_old=True):
        if not quick or self.layer_blocks_imgs_qt[self.selected_layer] is None:
            self.layer_blocks_imgs_qt[self.selected_layer] = ImageQt.ImageQt(
                self.loaded_map.get_blocks_full_img(self.selected_layer)
            )

        self.layer_blocks_pixmaps[self.selected_layer] = QtGui.QPixmap.fromImage(
            self.layer_blocks_imgs_qt[self.selected_layer]
        )

        if delete_old:
            self.ui.layer_blocks_scene.clear()
            self.layer_blocks_pixmap_qobjects[self.selected_layer] = qmapview.QMapPixmap(
                self.layer_blocks_pixmaps[self.selected_layer]
            )
            self.ui.layer_blocks_scene.addItem(self.layer_blocks_pixmap_qobjects[self.selected_layer])

            self.layer_blocks_pixmap_qobjects[self.selected_layer].clicked.connect(
                self.blocks_img_clicked
            )
        else:
            self.layer_blocks_pixmap_qobjects[self.selected_layer].set_pixmap(
                self.layer_blocks_pixmaps[self.selected_layer]
            )
        self.ui.layer_blocks_scene.update()

        draw_square_over_tile(self.layer_blocks_pixmaps[self.selected_layer], self.selected_block)
    #

    # Blocks Editor Tab

    def tileset_clicked(self):
        pass

    def print_tilesets(self):
        tileset_imgs = self.loaded_map.get_full_tileset_imgs(self.selected_palette, self.selected_layer)
        for i in range(2):
            self.ui.tileset_view_scenes[i].clear()
            self.tilesets_imgs_qt[i] = ImageQt.ImageQt(tileset_imgs[i])
            self.tileset_pixmaps[i] = QtGui.QPixmap.fromImage(self.tilesets_imgs_qt[i])
            self.tileset_pixmap_qobjects[i] = qmapview.QMapPixmap(self.tileset_pixmaps[i])
            self.ui.tileset_view_scenes[i].addItem(self.tileset_pixmap_qobjects[i])
            self.ui.tileset_view_scenes[i].update()

    def block_preview_clicked(self):
        pass

    def print_block_preview(self):
        pass

    def selected_palette_changed(self):
        self.selected_palette = self.ui.palette_combobox.currentIndex()
        self.print_tilesets()



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    r = app.exec_()
    app.deleteLater()
    sys.exit(r)

if __name__ == '__main__':
    main()
