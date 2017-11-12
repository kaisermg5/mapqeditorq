
from math import ceil
from PIL import Image

from mapqeditorq.game.structure_utils import StructureBase

BASE_TILE_16x16 = Image.new('RGB', (16, 16))
BASE_TILE_8x8 = Image.new('P', (8, 8))

MAPDATA_KEY = 0x324ae4


def is_final_encoded_pointer(pointer):
    return pointer & 0x80000000 == 0


def decode_mapdata_pointer(pointer):
    return (pointer & 0x7fffffff) + MAPDATA_KEY


def encode_mapdata_pointer(pointer, final=False):
    pointer -= MAPDATA_KEY
    if pointer < 0:
        raise Exception('Invalid mapdata address')
    if not final:
        pointer |= 0x80000000
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


def crop_img_in_tiles(img):
    w, h = img.size
    tiles_wide = w // 8
    tiles_high = h // 8
    tiles = [None] * (tiles_wide * tiles_high)

    c = 0
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            tiles[c] = img.crop((x, y, x + 8, y + 8))
            c += 1
    return tiles


class MapDataGenericHeader(StructureBase):
    FORMAT = (
        ('masked_data_ptr', 'u32'),     # If this is a palette header, it contains
                                        #   the palette header 2 index
        ('uncompress_address', 'u32'),  # If this is a palette header, it is 0
        ('uncompressed_size', 'u32')    # If this is a palette header, it is 0
    )

    def __init__(self):
        self.masked_data_ptr = None
        self.uncompress_address = None
        self.uncompressed_size = None

    def get_compressed_data_ptr(self):
        return decode_mapdata_pointer(self.masked_data_ptr)

    def set_compressed_data_ptr(self, new_pointer):
        final_flag = self.is_final()
        self.masked_data_ptr = encode_mapdata_pointer(new_pointer, final=final_flag)

    def is_final(self):
        return is_final_encoded_pointer(self.masked_data_ptr)

    def get_uncompressed_size(self):
        return self.uncompressed_size & 0x7ffffff

    def set_uncompressed_size(self, size):
        self.uncompressed_size = size | 0x80000000

    def is_palette_header(self):
        return self.uncompressed_size == 0 and self.uncompress_address == 0

    def get_palette_header2_index(self):
        return self.masked_data_ptr

    def set_palette_header2_index(self, index):
        self.masked_data_ptr = index

