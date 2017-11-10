
from math import ceil
from PIL import Image

from . import common


class BlocksObjectsCreator:
    POINTER_IDENTIFIER = {
        # RAM offset: (is_block_img_data, layer_num)
        #               if it is not data from the image,
        #               it is data from the behaviours
        0x202ceb4: (True, 0),
        0x2012654: (True, 1),
        0x202aeb4: (False, 0),
        0x2010654: (False, 1),
    }

    @classmethod
    def header_type_identifier(cls, header):
        return cls.POINTER_IDENTIFIER[header.uncompress_address]

    @classmethod
    def create_block_list(cls, game, map_index, layer_count=2):
        blocks = [Blocks() for i in range(layer_count)]

        i = 0
        while True:
            header_ptr = game.get_blocks_header_pointer(map_index, i)
            header = game.read_struct_at(header_ptr, common.MapDataGenericHeader)
            (is_block_img_data, layer_num) = cls.header_type_identifier(header)
            if is_block_img_data:
                blocks[layer_num].load(game, header, header_ptr)
            else:
                blocks[layer_num].load_behaviours(game, header, header_ptr)

            if header.is_final():
                break
            i += 1

        return blocks


class Blocks:
    POSITIONS = (
        (0, 0),
        (8, 0),
        (0, 8),
        (8, 8)
    )

    def __init__(self):
        self.header_ptr = None
        self.header = None
        self.original_compressed_size = None

        self.data = None
        self.imgs = None
        self.amount = None

        self.behaviours = BlocksBehaviour()

        self.modified = False

    def load(self, game, header, header_ptr):
        """self.header_ptr = game.get_blocks_header_pointer(map_index, blocks_index)
        self.header = game.read_struct_at(self.header_ptr, common.MapDataGenericHeader)"""
        self.header_ptr = header_ptr
        self.header = header
        self.load_data(game)

    def load_data(self, game):
        data_ptr = self.header.get_compressed_data_ptr()
        raw_data, self.original_compressed_size = game.read_compressed(data_ptr)
        self.amount = int(ceil(len(raw_data) / 8))
        self.data = [None] * self.amount
        for i in range(self.amount):
            block_raw_data = raw_data[i * 8:(i + 1) * 8]
            block_data = [None, None, None, None]
            for j in range(4):
                num = int.from_bytes(block_raw_data[j * 2:(j + 1) * 2], 'little')
                palette = num >> 12
                flip_x = (num >> 10) & 1
                flip_y = (num >> 11) & 1
                tile_num = num & 0x3ff
                block_data[j] = [tile_num, flip_x, flip_y, palette]
            self.data[i] = block_data

    def load_behaviours(self, game, header, header_ptr):
        self.behaviours.load(game, header, header_ptr)

    def load_imgs(self, map_object, layer_num):
        self.imgs = [None] * self.amount

        for i in range(self.amount):
            self.load_img_of_block(i, map_object, layer_num)

    def load_img_of_block(self, block_num, map_object, layer_num):
        block_data = self.data[block_num]
        img = common.BASE_TILE_16x16.copy()
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
            return common.BASE_TILE_16x16

    def set_block_data(self, block_num, block_part, data, map_object, layer_num):
        self.data[block_num][block_part] = data
        self.load_img_of_block(block_num, map_object, layer_num)
        self.modified = True

    def get_block_data(self, block_num):
        return self.data[block_num]

    def get_full_img(self):
        return common.draw_img_from_tileset(self.imgs, 8)

    def is_loaded(self):
        return self.data is not None and self.imgs is not None

    def was_modified(self):
        if not self.modified:
            return self.behaviours.was_modified()
        return True

    def to_bytes(self):
        raw_data = b''
        for block_data in self.data:
            block_raw_data = b''
            for block_part_data in block_data:
                tile_num, flip_x, flip_y, pal_num = block_part_data
                num = tile_num | (flip_x << 10) | (flip_y << 11) | pal_num << 12
                block_raw_data += num.to_bytes(2, 'little')
            raw_data += block_raw_data
        return raw_data

    def save_to_rom(self, game):
        if self.modified:
            data = self.to_bytes()
            old_offset = self.header.get_compressed_data_ptr()
            new_offset, self.original_compressed_size = game.alloc_modified_data(
                data,
                self.original_compressed_size,
                old_offset,
                compressed=True,
                start_address=common.MAPDATA_KEY
            )

            if old_offset != new_offset:
                self.header.set_compressed_data_ptr(new_offset)
                game.write(self.header_ptr, self.header.to_bytes())

            self.modified = False

        if self.behaviours.was_modified():
            self.behaviours.save_to_rom(game)

    def is_final(self):
        return self.header.is_final()

    def get_block_behaviours(self, block_num):
        return self.behaviours.get_data(block_num)

    def set_block_behaviours(self, block_num, value):
        self.behaviours.set_data(block_num, value)


class BlocksBehaviour:
    def __init__(self):
        self.header = None
        self.header_ptr = None
        self.data = None
        self.original_compressed_size = None
        self.modified = False

    def load(self, game, header, header_ptr):
        self.header = header
        self.header_ptr = header_ptr
        amount = self.header.get_uncompressed_size() // 2
        self.data = [None] * amount
        raw_data, self.original_compressed_size = game.read_compressed(self.header.get_compressed_data_ptr())

        for i in range(amount):
            self.data[i] = int.from_bytes(raw_data[2 * i:2 * i + 2], 'little')

    def save_to_rom(self, game):
        if self.was_modified():
            data = self.to_bytes()
            old_offset = self.header.get_compressed_data_ptr()
            new_offset, self.original_compressed_size = game.alloc_modified_data(
                data,
                self.original_compressed_size,
                old_offset,
                compressed=True,
                start_address=common.MAPDATA_KEY
            )

            if old_offset != new_offset:
                self.header.set_compressed_data_ptr(new_offset)
                game.write(self.header_ptr, self.header.to_bytes())

            self.modified = False

    def to_bytes(self):
        data = b''
        for halfword in self.data:
            data += halfword.to_bytes(2, 'little')
        return data

    def was_modified(self):
        return self.modified

    def set_data(self, block_num, value):
        if value != self.data[block_num]:
            self.data[block_num] = value
            if not self.modified:
                self.modified = True

    def get_data(self, block_num):
        return self.data[block_num]

