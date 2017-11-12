
from PIL import Image

from . import common


class MapLayerObjectsCeator:
    POINTER_IDENTIFIER = {
        # RAM offset: layer_num
        0x2025eb4: 0,
        0x200b654: 1,
    }

    @classmethod
    def create_map_layer_list(cls, game, map_index, map_subindex):
        map_layers = [MapLayer(), MapLayer()]

        i = 0
        while True:
            header_ptr = game.get_map_layer_header_pointer(map_index, map_subindex, i)
            header = game.read_struct_at(header_ptr, common.MapDataGenericHeader)

            # TODO: find out what the other data is...
            # check map 0x3, 0x1
            if header.uncompress_address in cls.POINTER_IDENTIFIER:
                layer_num = cls.POINTER_IDENTIFIER[header.uncompress_address]
                map_layers[layer_num].load(game, header, header_ptr)
            else:
                print(header)

            if header.is_final():
                break
            i += 1

        return map_layers


class MapLayer:
    def __init__(self):
        self.header_ptr = None
        self.header = None
        self.data = None
        self.original_compressed_size = None

        self.modified = False

    def load(self, game, header, header_ptr):
        self.header_ptr = header_ptr
        self.header = header

        self.load_data(game)

    def load_data(self, game):
        layer_data_ptr = self.header.get_compressed_data_ptr()
        raw_data, self.original_compressed_size = game.read_compressed(layer_data_ptr)
        self.load_from_raw(raw_data)

    def load_from_raw(self, raw_data):
        if self.data is not None and not self.was_modified():
            self.modified = True
        data_size = len(raw_data) // 2
        self.data = [None] * data_size

        for i in range(data_size):
            self.data[i] = int.from_bytes(raw_data[2 * i:2 * (i + 1)], 'little')

    def to_bytes(self):
        data = b''
        for block_num in self.data:
            data += block_num.to_bytes(2, 'little')
        return data

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
                delete_old=True
            )

            if old_offset != new_offset:
                self.header.set_compressed_data_ptr(new_offset)
                game.write(self.header_ptr, self.header.to_bytes())

            self.modified = False

    def was_modified(self):
        return self.modified

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
