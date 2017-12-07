# -*- coding: utf-8 -*-

import os
import sys
import time

from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore

from .editor_ui import Ui_MainWindow
from .new_project_dialog import NewProjectDialog
from ..mqeq_logic import common
from ..mqeq_logic.main_mqeq_handler import MainMqeqHandler
from .tilemap_scene import TilemapScene


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, filename=None):
        # Setup Window
        QtWidgets.QMainWindow.__init__(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(common.EDITOR_DIRECTORY, 'resources/mqeq-icon.ico'))
                       , QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create handler
        self.handler = MainMqeqHandler(self)

        # Connect menubar actions
        self.ui.action_New_Project.triggered.connect(self.new_project)
        self.ui.action_Open_Project.triggered.connect(lambda: self.open_project())
        self.ui.action_Save.triggered.connect(self.save)
        self.ui.export_blocks_action.triggered.connect(self.export_blocks)
        self.ui.import_blocks_action.triggered.connect(self.import_blocks)
        self.ui.export_blocks_behaviour_action.triggered.connect(self.export_blocks_behaviour)
        self.ui.import_blocks_behaviour_action.triggered.connect(self.import_blocks_behaviour)
        self.ui.import_map_layer_action.triggered.connect(self.import_map_layer)
        self.ui.export_map_layer_action.triggered.connect(self.export_map_layer)
        self.ui.actionMake.triggered.connect(self.make_project)
        self.ui.actionClean.triggered.connect(self.clean_project)

        self.ui.menuExport.setEnabled(False)
        self.ui.menuImport.setEnabled(False)

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

        # Setup Tileset editor tab
        self.ui.palette_combobox2.currentIndexChanged.connect(self.mirrored_palette_combobox)

        self.palette_image_view_scene = TilemapScene(32, clicked_event=self.palette_image_clicked)
        self.ui.palette_image_view.setScene(self.palette_image_view_scene)

        self.ui.red_spinbox.valueChanged.connect(self.color_edited)
        self.ui.green_spinbox.valueChanged.connect(self.color_edited)
        self.ui.blue_spinbox.valueChanged.connect(self.color_edited)
        self.ui.save_color_button.clicked.connect(self.save_color)

        self.ui.load_pal_from_img_button.clicked.connect(self.load_palette_from_image)

        self.change_tileset_view_scene = TilemapScene(16)
        self.ui.change_tileset_view.setScene(self.change_tileset_view_scene)
        self.ui.tileset_num_combobox.currentIndexChanged.connect(self.select_tileset)

        self.ui.export_tileset_button.clicked.connect(self.export_tileset)
        self.ui.import_tileset_button.clicked.connect(self.import_tileset)

        # Palette 1 hurts my eyes...
        initial_palette = self.handler.get_selected_palette()
        self.ui.palette_combobox.setCurrentIndex(initial_palette)
        self.ui.palette_combobox2.setCurrentIndex(initial_palette)
        self.ui.palette_combobox.currentIndexChanged.connect(self.selected_palette_changed)

        self.ui.flipX_checkbox.clicked.connect(self.print_tile_preview)
        self.ui.flipY_checkbox.clicked.connect(self.print_tile_preview)

        self.ui.selected_tile_ledit.returnPressed.connect(self.direct_tile_selection)


        if filename is not None:
            self.open_project(filename)

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

    @staticmethod
    def yes_no_question(title, question):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setText(question)
        msgbox.setIcon(QtWidgets.QMessageBox.Question)
        msgbox.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        msgbox.setDefaultButton(QtWidgets.QMessageBox.No)
        return msgbox.exec() == QtWidgets.QMessageBox.Yes

    def save_file_dialog(self, title, file_type='All files (*)'):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, title,
            self.handler.settings.last_opened_path,
            file_type
        )
        return filename

    def open_file_dialog(self, title, file_type='All files (*)'):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, title,
            self.handler.settings.last_opened_path,
            file_type
        )
        return filename

    # Closing events
    def closeEvent(self, event):
        if self.close_map_confirm():
            self.handler.close()
            event.accept()
        else:
            event.ignore()

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
    def new_project(self):
        d = NewProjectDialog(self.handler)
        d.exec()
        d.deleteLater()
        if self.handler.is_project_opened():
            self.project_opened_prepare_gui()

    def open_project(self, filename=None):
        if filename is None:
            filename = self.open_file_dialog('Open Project', 'BZ Project (*.bzproj)')
        if filename:
            self.handler.load_project(filename)
            self.project_opened_prepare_gui()

    def project_opened_prepare_gui(self):
        self.clear_scenes()
        self.ui.centralwidget.setEnabled(True)
        self.ui.tabWidget.setEnabled(False)

    def save(self):
        if not self.handler.is_project_opened():
            self.statusbar_show('No project opened')
            return
        elif not self.handler.are_there_unsaved_changes():
            self.statusbar_show('No changes to save')
            return
        self.statusbar_show('Saving...')
        self.handler.save_changes()
        self.statusbar_show('Map saved')

    def export_blocks(self):
        filename = self.save_file_dialog('Export blocks')
        if filename:
            self.handler.export_blocks(filename)
            self.statusbar_show('Blocks exported successfully')

    def import_blocks(self):
        filename = self.open_file_dialog('Import blocks')
        if filename:
            self.handler.import_blocks(filename)
            self.print_block_preview()
            self.print_blocks_img()
            self.print_map()
            self.statusbar_show('Blocks imported successfully')

    def export_blocks_behaviour(self):
        filename = self.save_file_dialog('Export blocks behaviour')
        if filename:
            self.handler.export_blocks_behaviour(filename)
            self.statusbar_show('Blocks behaviour exported successfully')

    def import_blocks_behaviour(self):
        filename = self.open_file_dialog('Import blocks behaviour')
        if filename:
            self.handler.import_blocks_behaviour(filename)
            self.load_behaviour_value()
            self.statusbar_show('Blocks behaviour imported successfully')

    def export_map_layer(self):
        filename = self.save_file_dialog('Export map layer')
        if filename:
            self.handler.export_map_layer(filename)
            self.statusbar_show('Map layer exported successfully')

    def import_map_layer(self):
        filename = self.open_file_dialog('Import map layer')
        if filename:
            self.handler.import_map_layer(filename)
            self.print_map()
            self.statusbar_show('Map layer imported successfully')

    def import_tileset(self):
        self.setEnabled(False)
        filename = self.open_file_dialog('Open Image file', 'All files (*)')
        if filename:
            try:
                self.handler.replace_selected_tileset(filename)
                self.print_all()
                self.statusbar_show('Tileset imported successfully')
            except common.MqeqError as e:
                self.error_message('Error importing tileset', str(e))
        self.setEnabled(True)

    def export_tileset(self):
        filename = self.save_file_dialog('Save tileset image', 'PNG Image (*.png)')
        if filename:
            if not (filename.lower()).endswith('.png'):
                filename += '.png'
            self.handler.export_selected_tileset(filename)
            self.statusbar_show('Tileset exported successfully')

    def make_project(self):
        try:
            self.handler.make_project()
        except Exception as e:
            self.error_message(type(e).__name__, str(e))

    def clean_project(self):
        try:
            self.handler.clean_project()
        except Exception as e:
            self.error_message(type(e).__name__, str(e))

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
        self.ui.menuImport.setEnabled(True)
        self.ui.menuExport.setEnabled(True)
        if not self.ui.tabWidget.isEnabled():
            self.ui.tabWidget.setEnabled(True)
        
    def print_all(self):
        self.print_map()
        self.print_blocks_img()
        self.print_tilesets()
        self.print_tile_preview()
        self.print_block_preview()
        self.print_selected_palette()
        self.print_change_tileset_preview()

    def select_layer(self, layer_num):
        self.handler.select_layer(layer_num)
        self.print_all()

        self.ui.layer1_button.setEnabled(layer_num != 0)
        self.ui.layer2_button.setEnabled(layer_num != 1)

    def clear_scenes(self):
        self.map_layer_scene.clear()
        self.layer_blocks_scene.clear()

        self.block_preview_scene.clear()
        self.tile_preview_scene.clear()
        for scene in self.tileset_view_scenes:
            scene.clear()

        self.palette_image_view_scene.clear()
        self.change_tileset_view_scene.clear()

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
        w, h = tile_img.size
        tile_img = tile_img.resize((h * 2, w * 2))

        self.tile_preview_scene.set_image(tile_img)

    def select_tile(self, tile_num):
        self.handler.select_tile(tile_num)
        self.update_tile_preview()

    def update_tile_preview(self):
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
            button = event.button()
            if button == QtCore.Qt.LeftButton:
                flip_x = self.ui.flipX_checkbox.isChecked()
                flip_y = self.ui.flipY_checkbox.isChecked()
                self.handler.paint_block(block_part, flip_x, flip_y)

                self.print_block_preview()
                self.print_blocks_img()
                self.print_map()
            elif button == QtCore.Qt.RightButton:
                flip_x, flip_y = self.handler.select_tile_at_block_part(block_part)
                self.ui.flipX_checkbox.setChecked(flip_x != 0)
                self.ui.flipY_checkbox.setChecked(flip_y != 0)
                self.ui.palette_combobox.setCurrentIndex(self.handler.get_selected_palette())
                self.update_tile_preview()

    def print_block_preview(self):
        block_img = self.handler.get_block_image()
        w, h = block_img.size
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
        if self.ui.palette_combobox2.currentIndex() != \
                self.ui.palette_combobox.currentIndex():
            self.ui.palette_combobox2.setCurrentIndex(
                self.ui.palette_combobox.currentIndex()
            )

        self.handler.set_selected_palette(self.ui.palette_combobox.currentIndex())
        self.print_tilesets()
        self.print_tile_preview()
        self.print_selected_palette()
        self.disable_enable_palette_modification_fields()
        self.print_change_tileset_preview()

    # Tileset editor tab
    def mirrored_palette_combobox(self):
        if self.ui.palette_combobox2.currentIndex() != \
                self.ui.palette_combobox.currentIndex():
            self.ui.palette_combobox.setCurrentIndex(
                self.ui.palette_combobox2.currentIndex()
            )

    def print_selected_palette(self):
        self.palette_image_view_scene.set_image(
            self.handler.get_selected_palette_image()
        )
        self.palette_image_view_scene.draw_square_over_tile(
            self.handler.get_selected_color()
        )
        self.load_selected_color_data()

    def palette_image_clicked(self, event):
        color_num = self.palette_image_view_scene.get_clicked_tile(event)
        if color_num != -1:
            self.select_color(color_num)

    def select_color(self, color_num):
        self.handler.select_color(color_num)
        self.print_selected_palette()

        if self.ui.save_color_button.isEnabled():
            self.ui.save_color_button.setEnabled(False)

    def load_selected_color_data(self):
        r, g, b = self.handler.get_selected_color_rgb_values()
        self.ui.red_spinbox.setValue(r)
        self.ui.green_spinbox.setValue(g)
        self.ui.blue_spinbox.setValue(b)
        self.ui.save_color_button.setEnabled(False)

    def disable_enable_palette_modification_fields(self):
        value = self.handler.is_palette_modification_allowed()

        self.ui.load_pal_from_img_button.setEnabled(value)
        self.ui.palette_color_groupbox.setEnabled(value)

    def load_palette_from_image(self):
        self.setEnabled(False)
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open Image file',
            self.handler.settings.last_opened_path,
            'All files (*)'
        )
        if filename:
            try:
                self.handler.load_palette_from_image(filename)
                self.print_all()
                self.statusbar_show('Palette imported successfully')
            except common.MqeqError as e:
                self.error_message('Error loading pal', str(e))
        self.setEnabled(True)

    def color_edited(self):
        if not self.ui.save_color_button.isEnabled():
            self.ui.save_color_button.setEnabled(True)

    def save_color(self):
        self.setEnabled(False)
        r = self.ui.red_spinbox.value()
        g = self.ui.green_spinbox.value()
        b = self.ui.blue_spinbox.value()
        self.handler.modify_selected_color((r, g, b))
        self.ui.save_color_button.setEnabled(False)

        self.print_all()
        self.setEnabled(True)

    def print_change_tileset_preview(self):
        self.change_tileset_view_scene.set_image(
            self.handler.get_selected_tileset_image()
        )

    def select_tileset(self):
        self.handler.select_tileset(self.ui.tileset_num_combobox.currentIndex())
        self.print_change_tileset_preview()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    r = app.exec_()
    app.deleteLater()
    sys.exit(r)

if __name__ == '__main__':
    main()
