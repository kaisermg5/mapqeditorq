
from mapqeditorq.game.game import Game
from mapqeditorq.maps.maps import Map
from . import settings

TILESET_MAX_SIZE = 512


class MainMqeqHandler:
    INITIAL_PALETTE = 2

    def __init__(self, gui):
        self.gui = gui

        self.settings = settings.UserSettings.load()

        # Define main attributes
        self.game = Game()
        self.loaded_map = None
        self.selected_tile = 0
        self.selected_block = 0
        self.selected_palette = self.INITIAL_PALETTE
        self.selected_layer = 0

    def save_settings(self):
        self.settings.save()

    def close(self):
        self.save_settings()
        self.game.close()
        return True

    def get_selected_block(self):
        return self.selected_block

    def get_selected_block_behaviours(self):
        return self.loaded_map.get_block_behaviours(self.selected_layer, self.selected_block)

    def set_selected_block_behaviours(self, value):
        return self.loaded_map.set_block_behaviours(self.selected_layer, self.selected_block, value)

    def get_adjusted_selected_tile(self):
        return self.selected_tile - (0, TILESET_MAX_SIZE)[self.get_selected_tile_tileset()]

    def get_selected_tile(self):
        return self.selected_tile

    def get_selected_tile_tileset(self):
        return self.selected_tile >= TILESET_MAX_SIZE

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
        new_loaded_map = Map()
        new_loaded_map.load(index, subindex, self.game)
        self.loaded_map = new_loaded_map

    def save_changes(self):
        self.loaded_map.save_to_rom(self.game)

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

