
from mapqeditorq.game import gba_image
from mapqeditorq.game.structure_utils import StructureBase
from . import common

from PIL import Image


class PaletteHeader2(StructureBase):
    FORMAT = (
        ('pal_index', 'u16'),
        ('unk1', 'u8'),
        ('unk2', 'u8')
    )

    def __init__(self):
        self.pal_index = None
        self.unk1 = None
        self.unk2 = None


class Palettes:
    PALETTE_IMG = Image.new('P', (8, 2))
    PALETTE_IMG.putdata(list(range(16)))
    PALETTE_IMG = PALETTE_IMG.resize((256, 64))

    def __init__(self):
        self.header1 = None
        self.header1_ptr = None
        self.header2 = None

        self.palettes_list = [None] * 16
        self.palettes_imgs = [None] * 16
        self.palettes_mod_count = [0] * 16
        self.modified = False

    def load(self, game, header, header_ptr):
        self.header1 = header
        self.header1_ptr = header_ptr
        header2_ptr = game.get_palette_header2_pointer(self.header1.get_palette_header2_index())
        self.header2 = game.read_struct_at(header2_ptr, PaletteHeader2)

        self.load_shared_palettes(game)

        # Load map palettes
        for i in range(13):
            palette_ptr = game.get_palette_pointer(self.header2.pal_index + i)
            palette_data = game.read(palette_ptr, 32)
            self.palettes_list[i + 2] = common.palette_from_gba_to_rgb(palette_data)

    def load_shared_palettes(self, game):
        # Load palettes shared by all maps
        for pal_index, table_index in ((0, 0), (1, 1), (15, 12)):
            palette_ptr = game.get_palette_pointer(table_index)
            palette_data = game.read(palette_ptr, 32)
            self.palettes_list[pal_index] = common.palette_from_gba_to_rgb(palette_data)

    def get_palette(self, index):
        return self.palettes_list[index]

    def get_palette_img(self, index):
        if self.palettes_imgs[index] is None:
            self.palettes_imgs[index] = self.PALETTE_IMG.copy()
            self.palettes_imgs[index].putpalette(self.palettes_list[index])
        return self.palettes_imgs[index]

    def was_modified(self):
        return self.modified

    def save_to_rom(self, game):
        if self.was_modified():
            for i in range(13):
                data = gba_image.palette_to_gba(self.palettes_list[i + 2])
                palette_ptr = game.get_palette_pointer(self.header2.pal_index + i)
                game.write(palette_ptr, data)

            self.modified = False

    def get_mod_count(self, pal_num):
        return self.palettes_mod_count[pal_num]

    def set_palette_modified(self, pal_num):
        if not self.was_modified():
            self.modified = True
        self.palettes_mod_count[pal_num] += 1
        self.palettes_imgs[pal_num].putpalette(self.palettes_list[pal_num])

    def set_palette(self, palette_num, palette):
        self.palettes_list[palette_num] = palette
        self.palettes_mod_count[palette_num] += 1
        self.set_palette_modified(palette_num)

    def set_color(self, pal_num, color_num, rgb):
        r, g, b = rgb
        self.palettes_list[pal_num][color_num * 3:(color_num + 1) * 3] = [r, g, b]
        self.set_palette_modified(pal_num)

    def get_color(self, pal_num, color_num):
        return self.palettes_list[pal_num][color_num * 3:(color_num + 1) * 3]

    def switch_color(self, pal_num, color1, color2):
        rgb1 = self.get_color(pal_num, color1)
        self.set_color(pal_num, color1, self.get_color(pal_num, color2))
        self.set_color(pal_num, color2, rgb1)











