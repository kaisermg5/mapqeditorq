
import threading

from mapqeditorq.game.structure_utils import StructureBase
from . import common
from . import blocks
from .tilesets import Tileset
from .map_layer import MapLayerObjectsCeator
from .palettes import Palettes


class MapHeader(StructureBase):
    FORMAT = (
        ('unk1', 's16'),  # If the first one is equal to -1
        ('unk2', 'u16'),
        ('tiles_wide', 'u16'),
        ('tiles_high', 'u16'),
        ('tileset_subindex', 'u16'),  # Must be less than 0xffff
    )

    def __init__(self):
        self.unk1 = None
        self.unk2 = None
        self.tiles_high = None
        self.tiles_wide = None
        self.tileset_subindex = None

    def get_tiles_high(self):
        return self.tiles_high >> 4

    def get_tiles_wide(self):
        return self.tiles_wide >> 4


class Map:
    def __init__(self):
        self.layers = None
        self.index = None
        self.subindex = None
        self.header = None

        self.palettes = Palettes()

        self.tilesets = None

        self.blocks = None

    def load(self, index, subindex, game):
        self.index = index
        self.subindex = subindex

        load_data_thread = threading.Thread(target=self.load_layers, args=(game,))
        load_data_thread.start()

        header_data_ptr = game.get_map_header_pointer(index, subindex)
        if header_data_ptr < 0:
            raise Exception('This map does not exist.')
        self.header = game.read_struct_at(header_data_ptr, MapHeader)
        if self.header.tiles_wide <= 0 or self.header.tiles_high <= 0:
            raise Exception('Not a valid map')

        load_tilesets_thread = threading.Thread(target=self.load_tilesets, args=(game,))
        load_tilesets_thread.start()

        self.load_blocks_data(game)

        load_tilesets_thread.join()
        self.load_blocks_imgs()

        load_data_thread.join()
        # print('scripts:', hex(game.get_scripts_array_ptr(index, subindex)))
        # print('warps:', hex(game.get_warps_array_ptr(index, subindex)))

    def load_layers(self, game):
        self.layers = MapLayerObjectsCeator.create_map_layer_list(game, self.index, self.subindex)

    def load_palettes(self, game, palette_header, header_ptr):
        self.palettes.load(game, palette_header, header_ptr)

    def load_tilesets(self, game):
        self.tilesets = []

        header_ptr = game.get_tilesets_and_palette_headers_array_ptr(
            self.index, self.header.tileset_subindex
        )

        tileset_headers = []
        header = game.read_struct_at(header_ptr, common.MapDataGenericHeader)
        while not header.is_palette_header():
            tileset_headers.append((header, header_ptr))
            header_ptr += header.size()
            header = game.read_struct_at(header_ptr, common.MapDataGenericHeader)
        self.load_palettes(game, header, header_ptr)

        for header, header_ptr in tileset_headers:
            tileset = Tileset()
            tileset.load(game, self.palettes, header, header_ptr)
            self.tilesets.append(tileset)

    def load_blocks_data(self, game):
        self.blocks = blocks.BlocksObjectsCreator.create_block_list(game, self.index)

    def load_blocks_imgs(self):
        load_layer2_imgs_th = threading.Thread(target=self.blocks[1].load_imgs, args=(self, 1))
        load_layer2_imgs_th.start()

        self.blocks[0].load_imgs(self, 0)

        load_layer2_imgs_th.join()

    def draw_layer(self, layer_num):
        tiles_wide = self.header.get_tiles_wide()
        tiles_high = self.header.get_tiles_high()

        return self.layers[layer_num].draw_img(self.blocks[layer_num], tiles_wide, tiles_high)

    def get_tile_img(self, pal_num, tile_num, layer_num):
        tileset_offset = 0
        while tile_num >= 512:
            tile_num -= 512
            tileset_offset += 1
        return self.tilesets[layer_num + tileset_offset].get_tile(pal_num, tile_num)

    def get_full_tileset_imgs(self, pal_num, layer_num):
        ret = ()
        for tileset in self.tilesets[layer_num:layer_num + 2]:
            ret += tileset.get_full_tileset(pal_num),
        return ret

    def get_tileset_image(self, pal_num, tilset_num):
        return self.tilesets[tilset_num].get_full_tileset(pal_num)

    def get_block_img(self, block_num, layer_num):
        return self.blocks[layer_num].get_block_img(block_num)

    def get_block_data(self, block_num, layer_num):
        return self.blocks[layer_num].get_block_data(block_num)

    def set_block_data(self, block_num, block_part, data, layer_num):
        self.blocks[layer_num].set_block_data(block_num, block_part, data, self, layer_num)

    def get_blocks_full_img(self, layer_num):
        return self.blocks[layer_num].get_full_img()

    def was_modified(self):
        for blocks_obj in self.blocks:
            if blocks_obj.was_modified():
                return True
        for layer in self.layers:
            if layer.was_modified():
                return True
        for tileset in self.tilesets:
            if tileset.was_modified():
                return True
        if self.palettes.was_modified():
            return True
        return False

    def set_map_tile(self, layer_num, tile_num, block_num):
        self.layers[layer_num].set_tile(tile_num, block_num)

    def save_to_rom(self, game):
        for layer in self.layers:
            layer.save_to_rom(game)

        for blocks_obj in self.blocks:
            if blocks_obj.was_modified():
                blocks_obj.save_to_rom(game)

        if self.palettes.was_modified():
            self.palettes.save_to_rom(game)

        for tileset in self.tilesets:
            if tileset.was_modified():
                tileset.save_to_rom(game)

    def get_indexes(self):
        return self.index, self.subindex

    def get_block_behaviours(self, layer_num, block_num):
        return self.blocks[layer_num].get_block_behaviours(block_num)

    def set_block_behaviours(self, layer_num, block_num, value):
        self.blocks[layer_num].set_block_behaviours(block_num, value)

    def get_block_num_at(self, layer_num, tile_num):
        return self.layers[layer_num].get_block_num_at(tile_num)

    def change_tileset_image(self, tileset_num, img):
        self.tilesets[tileset_num].change_image(img)
        self.redraw_blocks()

    def get_palette_image(self, pal_num):
        return self.palettes.get_palette_img(pal_num)

    def set_palette(self, palette_num, palette):
        self.palettes.set_palette(palette_num, palette)
        self.redraw_blocks()

    def get_color_rgb_values(self, pal_num, color_num):
        return self.palettes.get_color(pal_num, color_num)

    def modify_color(self, pal_num, color_num, rgb):
        self.palettes.set_color(pal_num, color_num, rgb)
        self.redraw_blocks()

    def redraw_blocks(self, layer_num=None):
        iterable = ((layer_num,), range(2))[layer_num is None]
        for layer_num in iterable:
            self.blocks[layer_num].load_imgs(self, layer_num)

    def get_blocks_data(self, layer_num):
        return self.blocks[layer_num].to_bytes()

    def set_blocks_data(self, layer_num, raw_data):
        self.blocks[layer_num].load_from_raw(raw_data)
        self.redraw_blocks(layer_num)

    def get_blocks_behaviour_data(self, layer_num):
        return self.blocks[layer_num].get_behaviour_data()

    def set_blocks_behaviour_data(self, layer_num, raw_data):
        self.blocks[layer_num].set_behaviour_data(raw_data)

    def set_layer_data(self, layer_num, raw_data):
        self.layers[layer_num].load_from_raw(raw_data)

    def get_layer_data(self, layer_num):
        return self.layers[layer_num].to_bytes()