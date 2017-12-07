
import os.path

from ..gui.console_dialog import ConsoleDialog
from ..game import gba_image
from .bzproject import BzProj
from . import settings
from . import common
from .subprocess_reader import SubprocessReader

from PIL import Image
import subprocess


class MainMqeqHandler:
    LAZY_PEOPLE_FLAG = False

    def __init__(self, gui):
        self.gui = gui

        self.settings = settings.UserSettings.load()

        # Define main attributes
        self.project = None
        self.loaded_map = None
        self.selected_tile = 0
        self.selected_block = 0
        self.selected_palette = 2
        self.selected_layer = 0
        self.selected_color = 0
        self.selected_tileset = 0

        # For those windows users who don't want to install the dependencies
        if self.LAZY_PEOPLE_FLAG:
            self.add_windows_tools_to_path()

    def add_windows_tools_to_path(self):
        tools_path = os.path.join(
            common.EDITOR_DIRECTORY, 'windows_tools'
        )
        os.environ['Path'] = os.path.pathsep.join(
            [os.environ['Path'], common.EDITOR_DIRECTORY, tools_path]
        )

    def save_settings(self):
        self.settings.save()

    def new_project(self, rom_filename, project_dir, project_name):
        self.project = BzProj()
        self.project.create(rom_filename, project_dir, project_name)

    def load_project(self, filename):
        self.project = BzProj()
        self.loaded_map = None
        self.settings.last_opened_path = os.path.dirname(filename)

        self.project.load(filename)

    def make_project(self):
        reader = SubprocessReader(['make'])
        d = ConsoleDialog(reader)
        d.exec()
        d.deleteLater()

    def clean_project(self):
        reader = SubprocessReader(['make', 'clean'])
        d = ConsoleDialog(reader)
        d.exec()
        d.deleteLater()

    def is_project_opened(self):
        return self.project is not None

    def close(self):
        self.save_settings()
        if self.project is not None:
            self.project.close()

    def get_selected_block(self):
        return self.selected_block

    def get_selected_block_behaviours(self):
        return self.loaded_map.get_block_behaviours(self.selected_layer, self.selected_block)

    def set_selected_block_behaviours(self, value):
        return self.loaded_map.set_block_behaviours(self.selected_layer, self.selected_block, value)

    def get_adjusted_selected_tile(self):
        return self.selected_tile - (0, common.TILESET_MAX_SIZE)[self.get_selected_tile_tileset()]

    def get_selected_tile(self):
        return self.selected_tile

    def get_selected_tile_tileset(self):
        return self.selected_tile >= common.TILESET_MAX_SIZE

    def select_block(self, block_num):
        if block_num > 0xffff:
            block_num = 0
        self.selected_block = block_num

    def select_block_at(self, tile_num):
        self.selected_block = self.loaded_map.get_block_num_at(self.selected_layer, tile_num)

    def select_tile(self, tile_num):
        if tile_num > 0x3ff:
            tile_num = 0
        self.selected_tile = tile_num

    def are_there_unsaved_changes(self):
        return self.loaded_map is not None and self.loaded_map.was_modified()

    def is_map_already_loaded(self, index, subindex):
        return self.loaded_map is not None and self.loaded_map.get_indexes() == (index, subindex)

    def load_map(self, index, subindex):
        self.loaded_map = self.project.load_map(index, subindex)

    def save_changes(self):
        self.project.save_changes()

    def paint_map_tile(self, tile_num):
        self.loaded_map.set_map_tile(self.selected_layer, tile_num, self.selected_block)

    def get_map_image(self):
        return self.loaded_map.draw_layer(self.selected_layer)

    def get_blocks_image(self):
        return self.loaded_map.get_blocks_full_img(self.selected_layer)

    def get_tileset_images(self):
        return self.loaded_map.get_full_tileset_imgs(self.selected_palette, self.selected_layer)

    def get_tile_image(self):
        return self.loaded_map.get_tile_img(self.selected_palette,
                                            self.selected_tile,
                                            self.selected_layer)

    def paint_block(self, block_part, flip_x, flip_y):
        data = [self.selected_tile, flip_x, flip_y, self.selected_palette]
        if self.loaded_map.get_block_data(self.selected_block, self.selected_layer)[block_part] != data:
            self.loaded_map.set_block_data(self.selected_block, block_part, data, self.selected_layer)

    def get_block_image(self):
        return self.loaded_map.get_block_img(self.selected_block, self.selected_layer)

    def set_selected_palette(self, pal_num):
        self.selected_palette = pal_num & 0xf

    def select_layer(self, layer_num):
        self.selected_layer = layer_num

    def get_selected_palette_image(self):
        return self.loaded_map.get_palette_image(self.selected_palette)

    def is_palette_modification_allowed(self):
        return self.selected_palette not in (0, 1, 15)

    @staticmethod
    def open_image(filename):
        try:
            img = Image.open(filename)
        except FileNotFoundError:
            raise common.MqeqError('The file "{0}" does not exist'.format(filename))
        except OSError:
            raise common.MqeqError('Unknown image format'.format(filename))
        try:
            gba_image.validate_gbaimage(img)
        except gba_image.ImageFormatError as e:
            raise common.MqeqError(str(e))
        return img

    def load_palette_from_image(self, filename):
        if not self.is_palette_modification_allowed():
            raise common.MqeqError('This palette does not belong to the map')
        img = self.open_image(filename)

        self.loaded_map.set_palette(self.selected_palette, img.getpalette())

    def select_color(self, color_num):
        if color_num < 0 or color_num > 15:
            color_num = 0
        self.selected_color = color_num

    def get_selected_color(self):
        return self.selected_color

    def get_selected_color_rgb_values(self):
        return self.loaded_map.get_color_rgb_values(self.selected_palette, self.selected_color)

    def modify_selected_color(self, rgb):
        self.loaded_map.modify_color(self.selected_palette, self.selected_color, rgb)

    def get_selected_tileset_image(self):
        return self.loaded_map.get_tileset_image(self.selected_palette, self.selected_tileset)

    def select_tileset(self, tileset_num):
        if tileset_num < 0 or tileset_num > 2:
            tileset_num = 0
        self.selected_tileset = tileset_num

    def export_selected_tileset(self, filename):
        img = self.get_selected_tileset_image()
        w, h = img.size
        img = img.resize((w // 2, h // 2))
        img.save(filename, 'PNG')

    def replace_selected_tileset(self, filename):
        img = self.open_image(filename)
        w, h = img.size
        if w != 128 or h != 256:
            raise common.MqeqError('The tileset image size has to be 128x256 px')
        self.loaded_map.change_tileset_image(self.selected_tileset, img)

    def select_tile_at_block_part(self, block_part):
        self.selected_tile, flip_x, flip_y, self.selected_palette = self.loaded_map.get_block_data(
            self.selected_block, self.selected_layer
        )[block_part]
        return flip_x, flip_y

    def get_selected_palette(self):
        return self.selected_palette

    def export_blocks(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.loaded_map.get_blocks_data(self.selected_layer))

    def import_blocks(self, filename):
        with open(filename, 'rb') as f:
            raw_data = f.read()
        self.loaded_map.set_blocks_data(self.selected_layer, raw_data)

    def export_blocks_behaviour(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.loaded_map.get_blocks_behaviour_data(self.selected_layer))

    def import_blocks_behaviour(self, filename):
        with open(filename, 'rb') as f:
            raw_data = f.read()
        self.loaded_map.set_blocks_behaviour_data(self.selected_layer, raw_data)

    def export_map_layer(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.loaded_map.get_layer_data(self.selected_layer))

    def import_map_layer(self, filename):
        with open(filename, 'rb') as f:
            raw_data = f.read()
        self.loaded_map.set_layer_data(self.selected_layer, raw_data)

