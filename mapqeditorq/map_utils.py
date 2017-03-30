
from PIL import Image
from math import ceil
import threading
from random import randint

from .structure_utils import StructureBase
from . import lz77
from . import game_utils

WRONG_PALETTE = [255, 0, 255]
for i in range(15):
    WRONG_PALETTE.extend((randint(80, 255), randint(80, 255), randint(80, 255)))

BASE_TILE_8x8 = Image.new('P', (8, 8))
BASE_TILE_16x16 = Image.new('RGB', (16, 16))

MAPDATA_KEY = 0x324ae4

def decode_mapdata_pointer(pointer):
    return (pointer & 0x7fffffff) + MAPDATA_KEY


def encode_mapdata_pointer(pointer, final=False):
    print(hex(pointer))
    pointer -= MAPDATA_KEY
    if pointer < 0:
        raise Exception('Invalid mapdata address')
    if not final:
        pointer += 0x80000000
    return pointer


def palette_from_gba_to_rgb(data):
    rgb_palette = []
    for i in range(0, len(data), 2):
        halfword = int.from_bytes(data[i:i + 2], 'little')
        r = (halfword & 0x1f) << 3
        g = ((halfword >> 5) & 0x1f) << 3
        b = ((halfword >> 10) & 0x1f) << 3
        rgb_palette.extend((r, g, b))
    return rgb_palette


def draw_img_from_tileset(tileset, tiles_wide, img_mode='RGB'):
    tile_amount = len(tileset)
    w, h = tileset[0].size
    total_w = w * tiles_wide
    tiles_high = ceil(tile_amount / tiles_wide)
    total_h = h * tiles_high
    img = Image.new(img_mode, (total_w, total_h))
    for i in range(tile_amount):
        x = i % tiles_wide
        y = i // tiles_wide
        img.paste(tileset[i], (x * w, y * h, (x + 1) * w, (y + 1) * h))
    return img


class PaletteHeader(StructureBase):
    FORMAT = (
        ('pal_index', 'u16'),
        ('unk1', 'u8'),
        ('unk2', 'u8')
    )

    def __init__(self):
        self.pal_index = None
        self.unk1 = None
        self.unk2 = None


class MapHeader(StructureBase):
    FORMAT = (
        ('unk1', 'u16'),  # If first one is equal to 0xffff, it doesn't load the map
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
        self.offsets = []
        self.compressed_sizes = []

        self.index = None
        self.subindex = None
        self.header = MapHeader()
        self.data = [None, None]

        self.palette_header_index = None
        self.palettes = [WRONG_PALETTE] * 2 + ([None] * 13) + [WRONG_PALETTE]

        self.tilesets = None

        self.blocks = None

        self.modified = [False, False]

    def load(self, index, subindex, game):
        self.index = index
        self.subindex = subindex

        load_data_thread = threading.Thread(target=self.load_data, args=(game,))
        load_data_thread.start()

        header_data_ptr_to_subtable = game_utils.MAP_HEADER_TABLE + index * 4
        header_data_ptr = game.read_pointer(header_data_ptr_to_subtable) + subindex * 0xa
        header_data = game.read(header_data_ptr, 0xa)
        self.header.load_from_bytes(header_data)

        load_tilesets_thread = threading.Thread(target=self.load_tilesets, args=(game,))
        load_tilesets_thread.start()

        self.load_blocks_data(game)

        load_tilesets_thread.join()
        self.load_blocks_imgs()

        load_data_thread.join()

    def load_data(self, game):
        mapdata_subtable = game.read_pointer(game_utils.MAPDATA_TABLE + self.index * 4)
        mapdata_ptr_to_ptr = game.read_pointer(mapdata_subtable + self.subindex * 4)

        for i in range(2):
            mapdata_ptr = decode_mapdata_pointer(game.read_u32(mapdata_ptr_to_ptr))
            layer_data = []
            raw_data, compressed_size = lz77.decompress(game.read(mapdata_ptr, 0x10000))
            for j in range(0, len(raw_data), 2):
                layer_data.append(int.from_bytes(raw_data[j:j + 2], 'little'))

            self.offsets.append(mapdata_ptr)
            self.compressed_sizes.append(compressed_size)
            self.data[i] = layer_data
            mapdata_ptr_to_ptr += 0xc

    def load_palettes(self, game, palette_header_index):
        palette_header_ptr = game.read_pointer(game_utils.PALETTE_HEADER_TABLE + palette_header_index * 4)
        palette_header = PaletteHeader()
        palette_header.load_from_bytes(game.read(palette_header_ptr, 4))

        palette_ptr = game_utils.PALETTE_TABLE + palette_header.pal_index * 32
        for i in range(13):
            palette = game.read(palette_ptr, 32)
            palette = palette_from_gba_to_rgb(palette)
            self.palettes[i + 2] = palette
            palette_ptr += 32

        self.palette_header_index = palette_header_index

    def load_tilesets(self, game):
        tilesets = []

        tileset_subtable_ptr = game_utils.TILESETS_TABLE + self.index * 4
        tileset_subtable = game.read_pointer(tileset_subtable_ptr)

        tileset_ptr_to_ptr = game.read_pointer(tileset_subtable + self.header.tileset_subindex * 4)

        tileset_ptrs = []
        undefined_word = 0x80000000  # Could be a tileset or a palette
        while undefined_word & 0x80000000:
            undefined_word = game.read_u32(tileset_ptr_to_ptr)
            if game.read_u32(tileset_ptr_to_ptr + 4) == 0:
                self.load_palettes(game, undefined_word)
            else:
                tileset_ptrs.append(decode_mapdata_pointer(undefined_word))
            tileset_ptr_to_ptr += 0xc

        for tileset_pointer in tileset_ptrs:
            tileset = Tileset(tileset_pointer)
            tileset.load(game, self.palettes)
            tilesets.append(tileset)

            tileset_ptr_to_ptr += 0xc

        self.tilesets = tilesets

    def load_blocks_data(self, game):
        blocks_ptr_to_ptr = game.read_pointer(game_utils.BLOCKS_TABLE + 4 * self.index)
        blocks_ptr = 0x80000000
        blocks = []
        while blocks_ptr & 0x80000000:
            blocks_ptr = game.read_u32(blocks_ptr_to_ptr)
            actual_blocks_ptr = decode_mapdata_pointer(blocks_ptr)

            blocks_obj = Blocks(actual_blocks_ptr)
            blocks_obj.load_data(game)
            blocks.append(blocks_obj)

            blocks_ptr_to_ptr += 0xc

        # TODO: discover why are blocks [2] and [3] useful
        self.blocks = blocks

    def load_blocks_imgs(self):
        load_layer2_imgs_th = threading.Thread(target=self.blocks[1].load_imgs, args=(self, 1))
        load_layer2_imgs_th.start()

        self.blocks[0].load_imgs(self, 0)

        load_layer2_imgs_th.join()

    def draw_layer(self, layer_num):
        data_size = len(self.data[0])
        tiles_wide = self.header.get_tiles_wide()
        tiles_high = self.header.get_tiles_high()
        img = Image.new('RGB', (tiles_wide * 16, tiles_high * 16))

        for i in range(data_size):
            x = i % tiles_wide
            y = i // tiles_wide
            img.paste(self.get_block_img(self.data[layer_num][i], layer_num),
                      (x * 16, y * 16, (x + 1) * 16, (y + 1) * 16))
        return img

    def get_tile_img(self, pal_num, tile_num, layer_num):
        is_second_tileset = tile_num >= 512
        if is_second_tileset:
            tile_num -= 512

        return self.tilesets[layer_num + is_second_tileset].get_tile(pal_num, tile_num)

    def get_full_tileset_imgs(self, pal_num, layer_num):
        ret = ()
        for tileset in self.tilesets[layer_num:layer_num + 2]:
            ret += tileset.get_full_tileset(pal_num),
        return ret

    def get_block_img(self, block_num, layer_num):
        return self.blocks[layer_num].get_block_img(block_num)

    def get_block_data(self, block_num, layer_num):
        return self.blocks[layer_num].get_block_data(block_num)

    def get_blocks_full_img(self, layer_num):
        return self.blocks[layer_num].get_full_img()

    def layer_to_bytes(self, layer_num):
        data = b''
        for block_num in self.data[layer_num]:
            data += block_num.to_bytes(2, 'little')
        return lz77.compress(data)

    def was_modified(self, layer_num=None):
        if layer_num is None:
            return self.modified[0] or self.modified[1]
        return self.modified[layer_num]

    def set_map_tile(self, layer_num, tile_num, block_num):
        if self.data[layer_num][tile_num] != block_num:
            self.data[layer_num][tile_num] = block_num
            if not self.was_modified(layer_num):
                self.modified[layer_num] = True

    def save_to_rom(self, game):
        mapdata_subtable = game.read_pointer(game_utils.MAPDATA_TABLE + self.index * 4)
        mapdata_ptr_to_ptr = game.read_pointer(mapdata_subtable + self.subindex * 4)
        for layer_num in range(2):
            if self.was_modified(layer_num):
                layer_data = self.layer_to_bytes(layer_num)
                game.delete_data(self.offsets[layer_num], self.compressed_sizes[layer_num])
                if len(layer_data) <= self.compressed_sizes[layer_num]:
                    game.write(self.offsets[layer_num], layer_data)
                else:
                    layer_data_offset = game.write_at_free_space(layer_data, start_address=MAPDATA_KEY)
                    encoded_offset = encode_mapdata_pointer(layer_data_offset, layer_num)
                    game.write_u32(mapdata_ptr_to_ptr + (0, 0xc)[layer_num], encoded_offset)

    def get_indexes(self):
        return self.index, self.subindex


class Blocks:
    POSITIONS = (
        (0, 0),
        (8, 0),
        (0, 8),
        (8, 8)
    )

    def __init__(self, offset):
        self.offset = offset
        self.compressed_size = None

        self.data = None
        self.imgs = None
        self.amount = None

        self.full_img = None

    def load_data(self, game):
        raw_data, compressed_size = lz77.decompress(game.read(self.offset, 0x10000))
        amount = ceil(len(raw_data) / 8)
        data = [None] * amount

        for i in range(amount):
            block_raw_data = raw_data[i * 8:(i + 1) * 8]
            block_data = [None, None, None, None]
            for j in range(4):
                num = int.from_bytes(block_raw_data[j * 2:(j + 1) * 2], 'little')
                palette = num >> 12
                flip_x = (num >> 10) & 1
                flip_y = (num >> 11) & 1
                tile_num = num & 0x3ff
                block_data[j] = [tile_num, flip_x, flip_y, palette]
            data[i] = block_data

        self.data = data
        self.amount = amount

        self.compressed_size = compressed_size

    def load_imgs(self, map_object, layer_num):
        self.imgs = [None] * self.amount

        for i in range(self.amount):
            self.load_img_of_block(i, map_object, layer_num)
        self.full_img = draw_img_from_tileset(self.imgs, 8)

    def load_img_of_block(self, block_num, map_object, layer_num):
        block_data = self.data[block_num]
        img = BASE_TILE_16x16.copy()
        for i in range(4):
            pos_x, pos_y = Blocks.POSITIONS[i]
            tile = map_object.get_tile_img(block_data[i][3], block_data[i][0], layer_num)

            if block_data[i][1]:
                tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
            if block_data[i][2]:
                tile = tile.transpose(Image.FLIP_TOP_BOTTOM)

            img.paste(tile, (pos_x, pos_y, pos_x + 8, pos_y + 8))

        self.imgs[block_num] = img

    def get_block_img(self, block_num):
        try:
            return self.imgs[block_num]
        except IndexError:
            return BASE_TILE_16x16

    def get_block_data(self, block_num):
        return self.data[block_num]

    def get_full_img(self):
        return self.full_img

    def is_loaded(self):
        return self.data is not None and self.imgs is not None


class Tileset:
    def __init__(self, offset):
        self.offset = offset
        self.compressed_size = None

        self.paleted_tiles = [([None] * 512) for i in range(16)]
        self.no_palette_tiles = [None] * 512
        self.palettes_list_ref = None

        self.full_imgs = [None] * 16

    def load(self, game, palettes):
        img_data, compressed_size = lz77.decompress(game.read(self.offset, 0x10000))

        for i in range(len(img_data) // 32):
            tile_img_data = []
            for pixel_pair in img_data[i * 32:(i + 1) * 32]:
                tile_img_data.extend((pixel_pair & 0xf, pixel_pair >> 4))
            no_pal_tile = BASE_TILE_8x8.copy()
            no_pal_tile.putdata(tile_img_data)
            self.no_palette_tiles[i] = no_pal_tile

        self.palettes_list_ref = palettes
        self.compressed_size = compressed_size

    def get_tile(self, pal_num, tile_num):
        img = self.paleted_tiles[pal_num][tile_num]
        if img is None:
            self.load_paletted_tile(pal_num, tile_num)
            img = self.paleted_tiles[pal_num][tile_num]
        return img

    def load_paletted_tile(self, pal_num, tile_num):
        tile = self.no_palette_tiles[tile_num].copy()
        tile.putpalette(self.palettes_list_ref[pal_num])
        self.paleted_tiles[pal_num][tile_num] = tile

    def draw_imgs(self):
        base = draw_img_from_tileset(self.no_palette_tiles, 32, 'P')
        for i in range(16):
            img = base.copy()
            img.putpalette(self.palettes_list_ref[i])
            self.full_imgs[i] = img

    def is_loaded(self):
        return self.no_palette_tiles[0] is not None

    def get_full_tileset(self, palette_num):
        if self.full_imgs[0] is None:
            self.draw_imgs()
        return self.full_imgs[palette_num]
