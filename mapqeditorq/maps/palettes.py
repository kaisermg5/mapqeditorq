
from mapqeditorq.game.structure_utils import StructureBase
from . import common


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
    def __init__(self):
        self.header1 = None
        self.header2 = None

        self.palettes_list = [None] * 16

    def load(self, game, header):
        self.header1 = header
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












