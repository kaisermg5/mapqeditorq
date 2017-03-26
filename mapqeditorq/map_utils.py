
from PIL import Image
from math import ceil
import threading
from random import randint

try:
    from .structure_utils import StructureBase
    from . import lz77
    from . import game_utils
except SystemError:
    from structure_utils import StructureBase
    import lz77
    import game_utils

WRONG_PALETTE = [255, 0, 255]
for i in range(15):
    WRONG_PALETTE.extend((randint(80, 255), randint(80, 255), randint(80, 255)))

BASE_TILE_8x8 = Image.new('P', (8, 8))
BASE_TILE_16x16 = Image.new('RGB', (16, 16))


def decode_mapdata_pointer(pointer):
    return (pointer & 0x7fffffff) + 0x324ae4


def palette_from_gba_to_rgb(data):
    rgb_palette = []
    for i in range(0, len(data), 2):
        halfword = int.from_bytes(data[i:i + 2], 'little')
        r = (halfword & 0x1f) << 3
        g = ((halfword >> 5) & 0x1f) << 3
        b = ((halfword >> 10) & 0x1f) << 3
        rgb_palette.extend((r, g, b))
    return rgb_palette


def draw_img_from_tileset(tileset, tiles_wide):
    tile_amount = len(tileset)
    w, h = tileset[0].size
    total_w = w * tiles_wide
    tiles_high = ceil(tile_amount / tiles_wide)
    total_h = h * tiles_high
    img = Image.new('RGB', (total_w, total_h))
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
        self.index = None
        self.subindex = None
        self.header = MapHeader()
        self.data = [None, None]
        self.imgs = None

        self.palette_header_index = None
        self.palettes = [WRONG_PALETTE] * 2 + ([None] * 13) + [WRONG_PALETTE]

        self.tilesets = None
        self.full_tileset = None

        self.blocks = None
        self.block_imgs = None

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
        self.load_blocks_imgs(self.full_tileset)

        load_data_thread.join()
        self.draw_imgs()

    def load_data(self, game):
        mapdata_subtable = game.read_pointer(game_utils.MAPDATA_TABLE + self.index * 4)
        mapdata_ptr_to_ptr = game.read_pointer(mapdata_subtable + self.subindex * 4)

        for i in range(2):
            mapdata_ptr = decode_mapdata_pointer(game.read_u32(mapdata_ptr_to_ptr))
            layer_data = []
            raw_data, _ = lz77.decompress(game.read(mapdata_ptr, 0x10000))
            for j in range(0, len(raw_data), 2):
                layer_data.append(int.from_bytes(raw_data[j:j + 2], 'little'))
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
        full_tileset = [[] for i in range(16)]

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
            tileset = Tileset()
            tileset.load(game, tileset_pointer, self.palettes)
            tilesets.append(tileset)

            tileset_ptr_to_ptr += 0xc

            for j in range(16):
                full_tileset[j].extend(tileset.tiles[j])

        self.tilesets = tilesets
        self.full_tileset = full_tileset

    def load_blocks_data(self, game):
        blocks_ptr_to_ptr = game.read_pointer(game_utils.BLOCKS_TABLE + 4 * self.index)
        blocks_ptr = 0x80000000
        blocks = []
        while blocks_ptr & 0x80000000:
            blocks_ptr = game.read_u32(blocks_ptr_to_ptr)
            actual_blocks_ptr = decode_mapdata_pointer(blocks_ptr)

            blocks_obj = Blocks()
            blocks_obj.load_data(game, actual_blocks_ptr)
            blocks.append(blocks_obj)

            blocks_ptr_to_ptr += 0xc

        self.blocks = blocks

    def load_blocks_imgs(self, tiles):
        l1_block_imgs = []
        l2_block_imgs = []

        num_of_threads = len(self.blocks) - 1
        load_imgs_threads = [None] * num_of_threads

        for i in range(num_of_threads):
            th = threading.Thread(target=self.blocks[i].load_imgs, args=(tiles,))
            th.start()
            load_imgs_threads[i] = th
        self.blocks[-1].load_imgs(tiles)

        for th in load_imgs_threads:
            th.join()

        for blocks_obj in self.blocks:
            l1_block_imgs.extend(blocks_obj.l1_imgs)
            l2_block_imgs.extend(blocks_obj.l2_imgs)

        self.block_imgs = l1_block_imgs, l2_block_imgs

    def draw_imgs(self):
        data_size = len(self.data[0])
        tiles_wide = self.header.get_tiles_wide()
        tiles_high = self.header.get_tiles_high()
        base_img = Image.new('RGB', (tiles_wide * 16, tiles_high * 16))
        self.imgs = [base_img, base_img.copy()]

        for i in range(2):
            for j in range(data_size):
                x = j % tiles_wide
                y = j // tiles_wide
                self.imgs[i].paste(self.block_imgs[i][self.data[i][j] + (0, self.blocks[0].amount)[i]],
                                   (x * 16, y * 16, (x + 1) * 16, (y + 1) * 16))


class Blocks:
    POSITIONS = (
        (0, 0),
        (8, 0),
        (0, 8),
        (8, 8)
    )

    def __init__(self):
        self.data = None
        self.l1_imgs = None
        self.l2_imgs = None
        self.amount = None

    def load_data(self, game, offset):
        raw_data, _ = lz77.decompress(game.read(offset, 0x10000))
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

    def load_imgs(self, tiles):
        self.l1_imgs = [None] * self.amount
        self.l2_imgs = [None] * self.amount

        for i in range(self.amount):
            self.load_img_of_block(i, tiles)

    def load_img_of_block(self, block_num, tiles):
        block_data = self.data[block_num]
        bg1_img = BASE_TILE_16x16.copy()
        bg2_img = BASE_TILE_16x16.copy()
        for i in range(4):
            pos_x, pos_y = Blocks.POSITIONS[i]
            bg1_tile = tiles[block_data[i][3]][block_data[i][0]]
            bg2_tile = tiles[block_data[i][3]][512 + block_data[i][0]]

            if block_data[i][1]:
                bg1_tile = bg1_tile.transpose(Image.FLIP_LEFT_RIGHT)
                bg2_tile = bg2_tile.transpose(Image.FLIP_LEFT_RIGHT)
            if block_data[i][2]:
                bg1_tile = bg1_tile.transpose(Image.FLIP_TOP_BOTTOM)
                bg2_tile = bg2_tile.transpose(Image.FLIP_LEFT_RIGHT)

            bg1_img.paste(bg1_tile, (pos_x, pos_y, pos_x + 8, pos_y + 8))
            bg2_img.paste(bg2_tile, (pos_x, pos_y, pos_x + 8, pos_y + 8))

        self.l1_imgs[block_num] = bg1_img
        self.l2_imgs[block_num] = bg2_img


class Tileset:
    def __init__(self):
        self.tiles = [([None] * 512) for i in range(16)]

    def load(self, game, offset, palettes):
        # TODO: put actual values here
        img_data, _ = lz77.decompress(game.read(offset, 0x10000))

        for i in range(len(img_data) // 32):
            tile_img_data = []
            for pixel_pair in img_data[i * 32:(i + 1) * 32]:
                tile_img_data.extend((pixel_pair & 0xf, pixel_pair >> 4))
            no_pal_tile = BASE_TILE_8x8.copy()
            no_pal_tile.putdata(tile_img_data)
            for j in range(16):
                tile = no_pal_tile.copy()
                tile.putpalette(palettes[j])
                self.tiles[j][i] = tile


if __name__ == '__main__':
    import time
    game = game_utils.Game()
    game.load('../testing/bzme.gba')

    map_object = Map()
    map_index = 0x0
    map_subindex = 0x0
    t = time.time()
    map_object.load(map_index, map_subindex, game)
    print('loaded in:', time.time() - t)

    blocks = map_object.block_imgs
    for i in range(2):
        img = draw_img_from_tileset(blocks[i], 16)
        img.save('../testing/layer{}_blocks.png'.format(i + 1), 'PNG')

    for i in range(2):
        map_object.imgs[i].save('../testing/layer{}.png'.format(i + 1), 'PNG')

