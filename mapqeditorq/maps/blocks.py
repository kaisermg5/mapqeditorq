
from math import ceil
from PIL import Image

from . import common


class Blocks(common.MapDataObjectBase):
    POSITIONS = (
        (0, 0),
        (8, 0),
        (0, 8),
        (8, 8)
    )

    def __init__(self):
        super().__init__()
        self.data = None
        self.imgs = None
        self.amount = None

        self.behaviours = BlocksBehaviour()

        self.modified = False

    def set_data(self, data):
        if self.data is not None and not self.was_modified():
            self.modified = True
        self.amount = int(ceil(len(data) / 8))
        self.data = [None] * self.amount
        for i in range(self.amount):
            block_raw_data = data[i * 8:(i + 1) * 8]
            block_data = [None, None, None, None]
            for j in range(4):
                num = int.from_bytes(block_raw_data[j * 2:(j + 1) * 2], 'little')
                palette = num >> 12
                flip_x = (num >> 10) & 1
                flip_y = (num >> 11) & 1
                tile_num = num & 0x3ff
                block_data[j] = [tile_num, flip_x, flip_y, palette]
            self.data[i] = block_data

    def get_behaviours_object(self):
        return self.behaviours

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

    def set_modified(self, value):
        self.modified = value

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

    def is_final(self):
        return self.header.is_final()

    def get_block_behaviours(self, block_num):
        return self.behaviours.get_data(block_num)

    def set_block_behaviours(self, block_num, value):
        self.behaviours.set_block_behaviour(block_num, value)

    def get_behaviour_data(self):
        return self.behaviours.to_bytes()

    def set_behaviour_data(self, raw_data):
        self.behaviours.load(raw_data)


class BlocksBehaviour(common.MapDataObjectBase):
    def __init__(self):
        super().__init__()
        self.data = None
        self.modified = False

    def set_data(self, data):
        if self.data is not None and not self.was_modified():
            self.modified = True
            amount = len(data) // 2
        else:
            amount = self.header.get_uncompressed_size() // 2
        self.data = [None] * amount
        for i in range(amount):
            self.data[i] = int.from_bytes(data[2 * i:2 * i + 2], 'little')

    def to_bytes(self):
        data = b''
        for halfword in self.data:
            data += halfword.to_bytes(2, 'little')
        return data

    def was_modified(self):
        return self.modified

    def set_modified(self, value):
        self.modified = value

    def set_block_behaviour(self, block_num, value):
        if value != self.data[block_num]:
            self.data[block_num] = value
            if not self.modified:
                self.modified = True

    def get_data(self, block_num):
        return self.data[block_num]

