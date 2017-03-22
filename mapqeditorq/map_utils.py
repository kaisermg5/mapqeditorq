
from PIL import Image

try:
    from .structure_utils import StructureBase
    from . import lz77
    from . import game_utils
except SystemError:
    from structure_utils import StructureBase
    import lz77
    import game_utils

GREYSCALE_PALETTE = []
for i in range(16):
    x = i * 17
    GREYSCALE_PALETTE.extend((x, x, x))
del x, i

BASE_TILE_8x8 = Image.new('P', (8, 8))
BASE_TILE_16x16 = Image.new('RGB', (16, 16))


def decode_mapdata_pointer(pointer):
    return (pointer & 0x7fffffff) + 0x324ae4


class MapHeader(StructureBase):
    FORMAT = (('unk1', 'u16'),  # If first one is equal to 0xffff, it doesn't load the map
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

    def load_tilesets(self, game):
        tilesets = []
        tileset_subtable_ptr = game_utils.TILESETS_TABLE + self.index * 4
        tileset_subtable = game.read_pointer(tileset_subtable_ptr)

        tileset_ptr_to_ptr = game.read_pointer(tileset_subtable + self.header.tileset_subindex * 4)
        # TODO: check if this actually works like this...
        tileset_pointer = 0x80000000
        while tileset_pointer & 0x80000000:
            tileset_pointer = game.read_u32(tileset_ptr_to_ptr)
            tileset = Tileset()
            try:
                tileset.load(game, decode_mapdata_pointer(tileset_pointer))
                tilesets.append(tileset)
            except lz77.InvalidLz77Data:
                print('Invalid Lz77 data at: {}'.format(hex(decode_mapdata_pointer(tileset_pointer))))

            tileset_ptr_to_ptr += 0xc

        self.tilesets = tilesets

        full_tileset = []
        for i in range(16):
            same_palette = []
            for tileset in tilesets:
                same_palette.extend(tileset.tiles[i])
            full_tileset.append(same_palette)

        self.full_tileset =full_tileset

    def load_blocks(self, game):
        blocks_ptr_to_ptr = game.read_pointer(game_utils.BLOCKS_TABLE + 4 * self.index)
        blocks_ptr = 0x80000000
        blocks = []
        block_imgs = []
        while blocks_ptr & 0x80000000:
            print('a')
            blocks_ptr = decode_mapdata_pointer(game.read_u32(blocks_ptr_to_ptr))
            blocks_data, _ = lz77.decompress(game.rom_contents[blocks_ptr:blocks_ptr + 0x10000])

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
            palette = num >> 13
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

    def load(self, game, offset, is_compressed=True):
        # TODO: put actual values here
        if is_compressed:
            img_data, _ = lz77.decompress(game.rom_contents[offset:offset + 0x10000])
        else:
            img_data = game.rom_contents[offset:offset + 0x10000]

        tiles = []

        for i in range(0, len(img_data), 32):
            tile_img_data = []
            for pixel_pair in img_data[i:i + 32]:
                tile_img_data.extend((pixel_pair & 0xf, pixel_pair >> 4))
            tile = BASE_TILE_8x8.copy()
            tile.putdata(tile_img_data)
            tile.putpalette(GREYSCALE_PALETTE)
            tiles.append(tile)
        self.tiles = (tiles,) * 16


if __name__ == '__main__':
    game = game_utils.Game()
    game.load('../testing/bzme.gba')
    mapx22 = Map()
    mapx22.load(0x22, 0, game)
    for i in range(len(mapx22.block_imgs)):
        mapx22.block_imgs[i].save('../testing/imgs/{}.png'.format(i), 'PNG')



