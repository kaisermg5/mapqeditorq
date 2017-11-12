
from . import common
from mapqeditorq.game import gba_image


class Tileset:
    def __init__(self):
        self.header = None
        self.header_ptr = None
        self.original_compressed_size = None

        self.paleted_tiles = [([None] * 512) for i in range(16)]
        self.no_palette_tiles = [None] * 512
        self.palettes = None
        self.expected_pal_mod_count = [None] * 16

        self.full_imgs = [None] * 16
        self.no_palette_full = None

        self.modified = False

    def load(self, game, palettes, header, header_ptr):
        self.header_ptr = header_ptr
        self.header = header
        self.palettes = palettes
        self.initialize_palette_mod_count()
        img_data, self.original_compressed_size = game.read_compressed(self.header.get_compressed_data_ptr())

        for i in range(len(img_data) // 32):
            tile_img_data = []
            for pixel_pair in img_data[i * 32:(i + 1) * 32]:
                tile_img_data.extend((pixel_pair & 0xf, pixel_pair >> 4))
            no_pal_tile = common.BASE_TILE_8x8.copy()
            no_pal_tile.putdata(tile_img_data)
            self.no_palette_tiles[i] = no_pal_tile

    def initialize_palette_mod_count(self):
        for i in range(16):
            self.expected_pal_mod_count[i] = self.palettes.get_mod_count(i)

    def check_palette_mod_count(self, pal_num):
        actual_mod_count = self.palettes.get_mod_count(pal_num)
        if self.expected_pal_mod_count[pal_num] \
                != actual_mod_count:
            self.paleted_tiles[pal_num] = [None] * 512
            if self.full_imgs[pal_num] is not None:
                self.full_imgs[pal_num].putpalette(self.palettes.get_palette(pal_num))
            self.expected_pal_mod_count[pal_num] = actual_mod_count

    def get_tile(self, pal_num, tile_num):
        self.check_palette_mod_count(pal_num)
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
        if self.no_palette_full is None:
            self.no_palette_full = common.draw_img_from_tileset(self.no_palette_tiles, 16, 'P')
        h, w = self.no_palette_full.size
        base = self.no_palette_full.resize((h * 2, w * 2))
        for i in range(16):
            img = base.copy()
            img.putpalette(self.palettes.get_palette(i))
            self.full_imgs[i] = img

    def is_loaded(self):
        return self.no_palette_tiles[0] is not None

    def get_full_tileset(self, palette_num):
        self.check_palette_mod_count(palette_num)
        if self.full_imgs[palette_num] is None:
            self.draw_imgs()
        return self.full_imgs[palette_num]

    def change_image(self, img):
        gba_image.validate_gbaimage(img)
        self.paleted_tiles = [([None] * 512) for i in range(16)]
        self.no_palette_tiles = common.crop_img_in_tiles(img)
        self.modified = True
        self.no_palette_full = img
        self.draw_imgs()

    def was_modified(self):
        return self.modified

    def save_to_rom(self, game):
        if self.was_modified():
            data = self.to_bytes()
            old_offset = self.header.get_compressed_data_ptr()
            new_offset, self.original_compressed_size = game.alloc_modified_data(
                data,
                self.original_compressed_size,
                old_offset,
                compressed=True,
                start_address=common.MAPDATA_KEY,
            )

            if old_offset != new_offset:
                self.header.set_compressed_data_ptr(new_offset)
                game.write(self.header_ptr, self.header.to_bytes())

            self.modified = False

    def to_bytes(self):
        return gba_image.img_to_gba_16colors(self.no_palette_full)
