# -*- coding: utf-8 -*-

import os
import sys
import time

from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore

from mapqeditorq.gui.editor_ui import Ui_MainWindow
from mapqeditorq.mqeq_logic import settings
from mapqeditorq.mqeq_logic.main_mqeq_handler import MainMqeqHandler
from mapqeditorq.gui.tilemap_scene import TilemapScene


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Setup Window
        QtWidgets.QMainWindow.__init__(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(settings.EDITOR_DIRECTORY, 'resources/mqeq-icon.ico'))
                       , QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create handler
        self.handler = MainMqeqHandler(self)

        # Connect menubar actions
        self.ui.action_Open_ROM.triggered.connect(lambda: self.open_rom())
        self.ui.action_Save.triggered.connect(lambda: self.save())

        # Connect main widgets
        self.ui.map_index_ledit.returnPressed.connect(self.load_map)
        self.ui.map_subindex_ledit.returnPressed.connect(self.load_map)
        self.ui.loadmap_button.clicked.connect(self.load_map)
        self.ui.layer1_button.clicked.connect(lambda: self.select_layer(0))
        self.ui.layer2_button.clicked.connect(lambda: self.select_layer(1))

        # Setup Map Layers tab
        self.map_layer_scene = TilemapScene(
            16, clicked_event=self.map_clicked, clicked_dragged_event=self.map_clicked
        )
        self.ui.map_layer_view.setScene(self.map_layer_scene)

        self.layer_blocks_scene = TilemapScene(16, clicked_event=self.blocks_img_clicked)
        self.ui.blocks_view.setScene(self.layer_blocks_scene)

        self.ui.selected_block_ledit.returnPressed.connect(self.direct_block_selection)

        # Setup Blocks Editor tab
        self.ui.blocks_view_2.setScene(self.layer_blocks_scene)

        self.tileset_view_scenes = [
            TilemapScene(16, clicked_event=lambda event: self.tileset_clicked(event, 0)),
            TilemapScene(16, clicked_event=lambda event: self.tileset_clicked(event, 1))
        ]
        self.ui.tileset_view_1.setScene(self.tileset_view_scenes[0])
        self.ui.tileset_view_2.setScene(self.tileset_view_scenes[1])

        self.tile_preview_scene = TilemapScene(16)
        self.ui.selected_tile_view.setScene(self.tile_preview_scene)

        self.block_preview_scene = TilemapScene(
            16,
            clicked_event=self.block_preview_clicked,
            clicked_dragged_event=self.block_preview_clicked
        )
        self.ui.selected_block_view.setScene(self.block_preview_scene)

        self.ui.block_behaviours_ledit.returnPressed.connect(self.set_block_behaviours)
        self.ui.block_behaviours_ledit.textEdited.connect(self.behaviour_value_modified)
        self.block_behaviours_ledit_font = QtGui.QFont(self.ui.block_behaviours_ledit.font())

        # Palette 1 hurts my eyes...
        self.ui.palette_combobox.setCurrentIndex(self.handler.INITIAL_PALETTE)
        self.ui.palette_combobox.currentIndexChanged.connect(self.selected_palette_changed)

        self.ui.flipX_checkbox.clicked.connect(self.print_tile_preview)
        self.ui.flipY_checkbox.clicked.connect(self.print_tile_preview)

        self.ui.selected_tile_ledit.returnPressed.connect(self.direct_tile_selection)

    # Gui utils
    def statusbar_show(self, message):
        self.ui.statusbar.showMessage(message)

    def error_message(self, title, description):
        QtWidgets.QMessageBox.critical(self, title, description)

    @staticmethod
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

    # Closing events
    def closeEvent(self, event):
        if not self.close_map_confirm() or not self.handler.close():
            event.ignore()
        else:
            event.accept()

    def close_map_confirm(self):
        if self.handler.are_there_unsaved_changes():
            self.setEnabled(False)
            result = self.confirm_saving_dialog('The map has been modified')
            if result == QtWidgets.QMessageBox.Cancel:
                self.setEnabled(True)
                return False
            elif result == QtWidgets.QMessageBox.Save:
                self.save()
            self.setEnabled(True)
        return True

    # Menu options
    def open_rom(self, filename=None):
        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open ROM file',
                                                                self.handler.settings.last_opened_path,
                                                                'GBA ROM (*.gba);;All files (*)')
        if filename:
            self.handler.settings.last_opened_path = os.path.dirname(filename)

            self.statusbar_show('Loading Rom...')
            if self.handler.game.load(filename):
                # Warning game code doesn't match
                pass
            self.statusbar_show('Rom loaded')
            self.ui.centralwidget.setEnabled(True)
            self.ui.tabWidget.setEnabled(False)

    def save(self):
        if not self.handler.game.loaded():
            self.statusbar_show('Game not loaded')
            return
        elif not self.handler.are_there_unsaved_changes():
            self.statusbar_show('No changes to save')
            return
        self.statusbar_show('Saving...')
        self.handler.save_changes()
        self.statusbar_show('Map saved')

    # Load map
    def load_map(self):
        if not self.close_map_confirm():
            return
        try:
            map_index = int(self.ui.map_index_ledit.text(), base=16)
            map_subindex = int(self.ui.map_subindex_ledit.text(), base=16)
        except ValueError:
            self.error_message(
                'Error loading map',
                'Both map index and sub index must be hexadecimal numbers'
            )
            return
        if self.handler.is_map_already_loaded(map_index, map_subindex):
            self.statusbar_show('Map already loaded')
            return

        self.statusbar_show('Loading Map...')
        self.setEnabled(False)
        t = time.time()

        try:
            self.handler.load_map(map_index, map_subindex)
        except Exception as e:
            self.error_message('Error loading map', '{0}: {1}'.format(type(e).__name__, str(e)))
            self.statusbar_show('Failed to load the map')
            self.setEnabled(True)
            # raise e
            return

        self.statusbar_show(
            'Map loaded in {} seconds'.format(time.time() - t)
        )

        self.setEnabled(True)

        self.select_layer(0)
        self.load_behaviour_value()

        if not self.ui.tabWidget.isEnabled():
            self.ui.tabWidget.setEnabled(True)
        
    def print_all(self):
        self.print_map()
        self.print_blocks_img()
        self.print_tilesets()
        self.print_tile_preview()
        self.print_block_preview()

    def select_layer(self, layer_num):
        self.handler.select_layer(layer_num)
        self.print_all()

        self.ui.layer1_button.setEnabled(layer_num != 0)
        self.ui.layer2_button.setEnabled(layer_num != 1)

    # Map Layer tab
    def map_clicked(self, event):
        tile_num = self.map_layer_scene.get_clicked_tile(event)
        if tile_num != -1:
            button = event.button()
            if button == QtCore.Qt.LeftButton:
                self.handler.paint_map_tile(tile_num)
                self.print_map()
            elif button == QtCore.Qt.RightButton:
                self.handler.select_block_at(tile_num)
                self.update_blocks_data()

    def print_map(self):
        self.map_layer_scene.set_image(self.handler.get_map_image())

    def select_block(self, block_num):
        self.handler.select_block(block_num)
        self.update_blocks_data()

    def update_blocks_data(self):
        self.print_blocks_img()
        self.print_block_preview()
        self.ui.selected_block_ledit.setText(hex(self.handler.get_selected_block()))
        self.load_behaviour_value()

    def direct_block_selection(self):
        try:
            block_num = int(self.ui.selected_block_ledit.text(), base=16)
        except ValueError:
            block_num = 0
        self.select_block(block_num)

    def blocks_img_clicked(self, event):
        block_num = self.layer_blocks_scene.get_clicked_tile(event)
        if block_num != -1:
            self.select_block(block_num)

    def print_blocks_img(self):
        self.layer_blocks_scene.set_image(self.handler.get_blocks_image())
        self.layer_blocks_scene.draw_square_over_tile(self.handler.get_selected_block())

    # Blocks Editor Tab
    def tileset_clicked(self, event, tileset_num):
        tile_num = self.tileset_view_scenes[tileset_num].get_clicked_tile(event) + (0, 512)[tileset_num]
        if tile_num != -1:
            self.select_tile(tile_num)

    def print_tilesets(self):
        tileset_imgs = self.handler.get_tileset_images()
        for i in range(2):
            self.tileset_view_scenes[i].set_image(tileset_imgs[i])

        selected_tile_tileset = self.handler.get_selected_tile_tileset()
        self.tileset_view_scenes[selected_tile_tileset].draw_square_over_tile(
            self.handler.get_adjusted_selected_tile()
        )

    def print_tile_preview(self):
        tile_img = self.handler.get_tile_image()

        if self.ui.flipX_checkbox.isChecked():
            tile_img = tile_img.transpose(Image.FLIP_LEFT_RIGHT)
        if self.ui.flipY_checkbox.isChecked():
            tile_img = tile_img.transpose(Image.FLIP_TOP_BOTTOM)
        h, w = tile_img.size
        tile_img = tile_img.resize((h * 2, w * 2))

        self.tile_preview_scene.set_image(tile_img)

    def select_tile(self, tile_num):
        self.handler.select_tile(tile_num)
        self.print_tilesets()
        self.print_tile_preview()
        self.ui.selected_tile_ledit.setText(hex(self.handler.get_selected_tile()))

    def direct_tile_selection(self):
        try:
            tile_num = int(self.ui.selected_tile_ledit.text(), base=16)
        except ValueError:
            tile_num = 0
        self.select_tile(tile_num)

    def block_preview_clicked(self, event):
        block_part = self.block_preview_scene.get_clicked_tile(event)
        if block_part != -1:
            flip_x = self.ui.flipX_checkbox.isChecked()
            flip_y = self.ui.flipY_checkbox.isChecked()
            self.handler.paint_block(block_part, flip_x, flip_y)

            self.print_block_preview()
            self.print_blocks_img()
            self.print_map()

    def print_block_preview(self):
        block_img = self.handler.get_block_image()
        h, w = block_img.size
        block_img = block_img.resize((h * 2, w * 2))
        self.block_preview_scene.set_image(block_img)

    def set_block_behaviours(self):
        try:
            value = int(self.ui.block_behaviours_ledit.text(), base=16)
            if 0 <= value <= 0xffff:
                self.handler.set_selected_block_behaviours(value)
                self.load_behaviour_value()
            else:
                self.error_message(
                    'Error setting block behaviour',
                    'Behaviour value must be number between 0x0 and 0xffff'
                )
        except ValueError:
            self.error_message(
                'Error setting block behaviour',
                'Invalid hexadecimal value'
            )

    def load_behaviour_value(self):
        self.ui.block_behaviours_ledit.setText(hex(self.handler.get_selected_block_behaviours()))
        self.block_behaviours_ledit_font.setBold(False)
        self.ui.block_behaviours_ledit.setFont(self.block_behaviours_ledit_font)

    def behaviour_value_modified(self):
        self.block_behaviours_ledit_font.setBold(True)
        self.ui.block_behaviours_ledit.setFont(self.block_behaviours_ledit_font)

    def selected_palette_changed(self):
        self.handler.set_selected_palette(self.ui.palette_combobox.currentIndex())
        self.print_tilesets()
        self.print_tile_preview()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    r = app.exec_()
    app.deleteLater()
    sys.exit(r)

if __name__ == '__main__':
    main()
