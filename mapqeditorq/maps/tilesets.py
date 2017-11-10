from PIL import Image

from . import common


class Tileset:
    def __init__(self):
        self.header = None
        self.compressed_size = None

        self.paleted_tiles = [([None] * 512) for i in range(16)]
        self.no_palette_tiles = [None] * 512
        self.palettes = None

        self.full_imgs = [None] * 16

    def load(self, game, palettes, header):
        self.header = header
        self.palettes = palettes
        img_data, self.compressed_size = game.read_compressed(self.header.get_compressed_data_ptr())

        for i in range(len(img_data) // 32):
            tile_img_data = []
            for pixel_pair in img_data[i * 32:(i + 1) * 32]:
                tile_img_data.extend((pixel_pair & 0xf, pixel_pair >> 4))
            no_pal_tile = common.BASE_TILE_8x8.copy()
            no_pal_tile.putdata(tile_img_data)
            self.no_palette_tiles[i] = no_pal_tile

    def get_tile(self, pal_num, tile_num):
        img = self.paleted_tiles[pal_num][tile_num]
        if img is None:
            self.load_paletted_tile(pal_num, tile_num)
            img = self.paleted_tiles[pal_num][tile_num]
        return img

    def load_paletted_tile(self, pal_num, tile_num):
        tile = self.no_palette_tiles[tile_num].copy()
        tile.putpalette(self.palettes.get_palette(pal_num))
        self.paleted_tiles[pal_num][tile_num] = tile

    def draw_imgs(self):
        base = common.draw_img_from_tileset(self.no_palette_tiles, 16, 'P')
        h, w = base.size
        base = base.resize((h * 2, w * 2))
        for i in range(16):
            img = base.copy()
            img.putpalette(self.palettes.get_palette(i))
            self.full_imgs[i] = img

    def is_loaded(self):
        return self.no_palette_tiles[0] is not None

    def get_full_tileset(self, palette_num):
        if self.full_imgs[palette_num] is None:
            self.draw_imgs()
        return self.full_imgs[palette_num]


class FakeTileset:
    img = Image.new('P', (16 * 16, 16 * 32))

    def __init__(self, offset=None):
        self.tile = common.BASE_TILE_8x8.copy()

    def load(self, game, palettes):
        pass

    def get_tile(self, pal_num, tile_num):
        return self.tile

    def load_paletted_tile(self, pal_num, tile_num):
        pass

    def draw_imgs(self):
        pass

    def is_loaded(self):
        return True

    def get_full_tileset(self, palette_num):
        return self.img


FAKE_TILESET = FakeTileset()

