
from PIL import Image

from . import common


class MapLayer(common.MapDataObjectBase):
    def __init__(self):
        super().__init__()
        self.data = None

        self.modified = False

    def set_data(self, data):
        if self.data is not None and not self.was_modified():
            self.modified = True
        data_size = len(data) // 2
        self.data = [None] * data_size

        for i in range(data_size):
            self.data[i] = int.from_bytes(data[2 * i:2 * (i + 1)], 'little')

    def to_bytes(self):
        data = b''
        for block_num in self.data:
            data += block_num.to_bytes(2, 'little')
        return data

    def was_modified(self):
        return self.modified

    def set_modified(self, value):
        self.modified = value

    def draw_img(self, blocks, tiles_wide, tiles_high):
        img = Image.new('RGB', (tiles_wide * 16, tiles_high * 16))

        for i in range(len(self.data)):
            x = i % tiles_wide
            y = i // tiles_wide
            img.paste(blocks.get_block_img(self.data[i]),
                      (x * 16, y * 16, (x + 1) * 16, (y + 1) * 16))
        return img

    def set_tile(self, tile_num, block_num):
        if self.data[tile_num] != block_num:
            self.data[tile_num] = block_num

            if not self.was_modified():
                self.modified = True

    def get_block_num_at(self, tile_num):
        return self.data[tile_num]
