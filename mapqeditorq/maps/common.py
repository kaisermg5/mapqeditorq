
import abc
from math import ceil
from PIL import Image
import re


from ..mqeq_logic.parsers import ParseableStructBase

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


class MapDataGenericHeader(ParseableStructBase):
    FORMAT = (
        ('masked_data_ptr', 'u32'),     # If this is a palette header, it contains
                                        #   the palette header 2 index
        ('uncompress_address', 'u32'),  # If this is a palette header, it is 0
        ('uncompressed_size', 'u32')    # If this is a palette header, it is 0
    )

    UNSPECTED_STR_TYPE = -2
    UNK_HEADER_TYPE = -1
    MAP_LAYER_1 = 0
    MAP_LAYER_2 = 1
    BLOCKS_1_IMG_DATA = 2
    BLOCKS_2_IMG_DATA = 3
    BLOCKS_1_BEHAVIOURS = 4
    BLOCKS_2_BEHAVIOURS = 5
    PALETTE = 6
    TILESET_1 = 7
    TILESET_2 = 8
    TILESET_3 = 9

    HEADER_TYPE_DICT = {
        0x2025eb4: MAP_LAYER_1,
        0x200b654: MAP_LAYER_2,
        0x202ceb4: BLOCKS_1_IMG_DATA,
        0x2012654: BLOCKS_2_IMG_DATA,
        0x202aeb4: BLOCKS_1_BEHAVIOURS,
        0x2010654: BLOCKS_2_BEHAVIOURS,
        0x6000000: TILESET_1,
        0x6004000: TILESET_2,
        0x6008000: TILESET_3,
    }

    def __init__(self):
        super().__init__()
        self.masked_data_ptr = None
        self.uncompress_address = None
        self.uncompressed_size = None

    def get_compressed_data_ptr(self):
        if isinstance(self.masked_data_ptr, int):
            return decode_mapdata_pointer(self.masked_data_ptr)
        else:
            m = re.match(r'.*_MAPDATA_PTR\((.*)\)', self.masked_data_ptr)
            return m.group(1)

    def set_compressed_data_ptr(self, new_pointer):
        final_flag = self.is_final()
        if isinstance(new_pointer, int):
            self.masked_data_ptr = encode_mapdata_pointer(new_pointer, final=final_flag)
        else:
            self.masked_data_ptr = (
                'MASK_MAPDATA_PTR({0})',
                'MASK_FINAL_MAPDATA_PTR({0})'
            )[final_flag].format(new_pointer)
        self.modified = True

    def is_final(self):
        if isinstance(self.masked_data_ptr, int):
            return is_final_encoded_pointer(self.masked_data_ptr)
        else:
            return 'MASK_FINAL_MAPDATA_PTR' in self.masked_data_ptr

    def get_uncompressed_size(self):
        return self.uncompressed_size & 0x7ffffff

    def set_uncompressed_size(self, size):
        self.uncompressed_size = size | 0x80000000
        self.modified = True

    def is_palette_header(self):
        return self.uncompress_address == 0

    def get_palette_header2_index(self):
        return self.masked_data_ptr

    def set_palettes_ptr(self, label):
        self.masked_data_ptr = label
        self.modified = True

    def set_palette_header2_index(self, index):
        self.masked_data_ptr = index
        self.modified = True

    def header_type(self):
        if isinstance(self.uncompress_address, str):
            return self.UNSPECTED_STR_TYPE
        elif self.uncompress_address < 0x1000000:
            return self.PALETTE
        elif self.uncompress_address not in self.HEADER_TYPE_DICT:
            return self.UNK_HEADER_TYPE
        else:
            return self.HEADER_TYPE_DICT[self.uncompress_address]


class MapDataObjectBase:
    def __init__(self):
        self.header = None

    def set_header(self, header):
        self.header = header

    @abc.abstractmethod
    def set_data(self, data):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def was_modified(self):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def set_modified(self, value):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def to_bytes(self):
        raise NotImplementedError('You must override this')



