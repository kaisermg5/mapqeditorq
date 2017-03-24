
from PIL import Image

try:
    from .structure_utils import StructureBase
    from . import lz77
    from . import game_utils
except SystemError:
    from structure_utils import StructureBase
    import lz77
    import game_utils

WRONG_PALETTE = [255, 0, 255] * 16

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
        ('unk3', 'u16'),  # Height?
        ('unk4', 'u16'),  # Width?
        ('tileset_subindex', 'u16'),  # Must be less than 0xffff
    )

    def __init__(self):
        self.unk1 = None
        self.unk2 = None
        self.unk3 = None
        self.unk4 = None
        self.tileset_subindex = None


class Map:
    def __init__(self):
        self.index = None
        self.subindex = None
        self.header = MapHeader()

        self.palette_header_index = None
        self.palettes = None

        self.tilesets = None
        self.full_tileset = None

        self.blocks = None
        self.block_imgs = None

    def load(self, index, subindex, game):
        header_data_ptr_to_ptr = game_utils.MAP_HEADER_TABLE + index * 4
        header_data_ptr = game.read_pointer(header_data_ptr_to_ptr + subindex * 4)
        header_data = game.rom_contents[header_data_ptr:header_data_ptr + 0xa]
        self.header.load_from_bytes(header_data)

        self.index = index

        self.load_tilesets(game)

        self.load_blocks(game)

    def load_palettes(self, game, palette_header_index):
        palette_header_ptr = game.read_pointer(game_utils.PALETTE_HEADER_TABLE + palette_header_index * 4)
        palette_header = PaletteHeader()
        palette_header.load_from_bytes(game.rom_contents[palette_header_ptr:palette_header_ptr + 4])

        palettes = [WRONG_PALETTE] * 2

        palette_ptr = game_utils.PALETTE_TABLE + palette_header.pal_index * 32
        for i in range(13):
            palette = game.rom_contents[palette_ptr:palette_ptr + 32]
            palette = palette_from_gba_to_rgb(palette)
            palettes.append(palette)
            palette_ptr += 32
        palettes.append(WRONG_PALETTE)

        self.palettes = palettes
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
            try:
                tileset.load(game, tileset_pointer, self.palettes)
                tilesets.append(tileset)
            except lz77.InvalidLz77Data:
                print('Invalid Lz77 data at: {}'.format(hex(tileset_pointer)))

            tileset_ptr_to_ptr += 0xc

            for j in range(16):
                full_tileset[j].extend(tileset.tiles[j])

        self.tilesets = tilesets
        self.full_tileset = full_tileset

    def load_blocks(self, game):
        blocks_ptr_to_ptr = game.read_pointer(game_utils.BLOCKS_TABLE + 4 * self.index)
        blocks_ptr = 0x80000000
        blocks = []
        block_imgs = []
        while blocks_ptr & 0x80000000:
            blocks_ptr = game.read_u32(blocks_ptr_to_ptr)
            actual_blocks_ptr = decode_mapdata_pointer(blocks_ptr)
            print('blocks:', hex(actual_blocks_ptr))
            blocks_data, _ = lz77.decompress(game.rom_contents[actual_blocks_ptr:actual_blocks_ptr + 0x10000])

            for i in range(0, len(blocks_data), 8):
                block = Block(blocks_data[i:i + 8])
                block_imgs.append(block.draw_img(self.full_tileset))
                blocks.append(block)

            blocks_ptr_to_ptr += 0xc

        self.blocks = blocks
        self.block_imgs = block_imgs


class Block:
    POSITIONS = (
        (0, 0),
        (8, 0),
        (0, 8),
        (8, 8)
    )

    def __init__(self, raw):
        data = [None, None, None, None]
        for i in range(4):
            num = int.from_bytes(raw[i * 2:(i + 1) * 2], 'little')
            palette = num >> 12
            flip_x = (num >> 10) & 1
            flip_y = (num >> 11) & 1
            tile_num = num & 0x3ff
            data[i] = [tile_num, flip_x, flip_y, palette]
        self.data = data

    def draw_img(self, tiles):
        img = BASE_TILE_16x16.copy()
        for i in range(4):
            pos_x, pos_y = Block.POSITIONS[i]
            tile = tiles[self.data[i][3]][self.data[i][0]]

            if self.data[i][1]:
                tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
            if self.data[i][2]:
                tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
            img.paste(tile, (pos_x, pos_y, pos_x + 8, pos_y + 8))
        return img


class Tileset:
    def __init__(self):
        self.tiles = None

    def load(self, game, offset, palettes, is_compressed=True):
        # TODO: put actual values here
        if is_compressed:
            img_data, _ = lz77.decompress(game.rom_contents[offset:offset + 0x10000])
            print('tileset:', hex(offset))
        else:
            img_data = game.rom_contents[offset:offset + 0x10000]

        tiles = [[] for i in range(16)]

        for i in range(0, len(img_data), 32):
            tile_img_data = []
            for pixel_pair in img_data[i:i + 32]:
                tile_img_data.extend((pixel_pair & 0xf, pixel_pair >> 4))
            no_pal_tile = BASE_TILE_8x8.copy()
            no_pal_tile.putdata(tile_img_data)
            for j in range(16):
                tile = no_pal_tile.copy()
                tile.putpalette(palettes[j])
                tiles[j].append(tile)
        self.tiles = tiles


if __name__ == '__main__':
    game = game_utils.Game()
    game.load('../testing/bzme.gba')
    map_object = Map()
    map_index = 0x22
    map_subindex = 0
    map_object.load(map_index, map_subindex, game)
    n = len(map_object.block_imgs)
    heig = round(n / 16 + 0.5)
    img = Image.new('RGB', (16 * 16, heig * 16))

    for i in range(n):
        w = i % 16
        h = i // 16
        img.paste(map_object.block_imgs[i], (w * 16, h * 16, (w + 1) * 16, (h + 1) * 16))

    img.save('../testing/blocks_map_{}_{}.png'.format(hex(map_index), hex(map_subindex)), 'PNG')




