
from mapqeditorq.game import lz77

from mapqeditorq.maps.maps import MapHeader
from mapqeditorq.maps.common import MapDataGenericHeader


class Game:
    # Game pointers
    MAP_HEADER_TABLE = 0x11e214

    TILESETS_TABLE = 0x10246c
    MAP_LAYER_HEADER_TABLE = 0x107988
    BLOCKS_TABLE = 0x10309c
    unk_table2 = 0xb755c
    WARPS_TABLE = 0x13a7f0
    SCRIPTs_TABLE = 0xd50fc

    PALETTE_HEADER2_TABLE = 0xff850
    PALETTE_TABLE = 0x5a2e80

    unk_table_5 = 0x127d30

    def __init__(self):
        self.file_object = None
        self.rom_contents_buffer = None

        self.modified = False

    def load(self, filename):
        self.file_object = open(filename, 'rb+')
        self.rom_contents_buffer = bytearray(self.file_object.read())
        if self.read(0xac, 4) != b'BZME':
            # Warning
            return 1
        return 0

    @staticmethod
    def pointer_mask(address):
        return address + 0x8000000

    @staticmethod
    def pointer_unmask(address):
        return address - 0x8000000

    def read(self, address, amount_of_bytes):
        if address < 0:
            raise Exception('"{}" is not a valid offset.'.format(address))
        return self.rom_contents_buffer[address:address + amount_of_bytes]

    def read_u32(self, address):
        return int.from_bytes(self.read(address, 4), 'little')

    def read_pointer(self, address):
        return self.pointer_unmask(self.read_u32(address))

    def find_free_space(self, size, start_address=0, aligned=True):
        if aligned:
            size += 3
        found_free_space = False
        while not found_free_space:
            address = self.rom_contents_buffer.find(b'\xff' * size, start_address)
            if address == -1:
                raise Exception('The ROM is out of space!')

            self.file_object.seek(address)
            actual_contents = self.file_object.read(size)
            if actual_contents == b'\xff' * size:
                found_free_space = True
            else:
                self.rom_contents_buffer[address:address + size] = actual_contents
        if aligned:
            address += (0, 3, 2, 1)[address % 4]
        return address

    def write(self, address, data):
        self.file_object.seek(address)
        self.file_object.write(data)
        self.rom_contents_buffer[address:address + len(data)] = data
        if not self.was_modified():
            self.modified = True

    def write_u32(self, address, num):
        self.write(address, num.to_bytes(4, 'little'))

    def write_at_free_space(self, data, start_address=0):
        data_size = len(data)
        free_space_address = self.find_free_space(data_size, start_address)
        self.write(free_space_address, data)

        return free_space_address

    def was_modified(self):
        return self.modified

    def delete_data(self, address, size):
        self.write(address, b'\xff' * size)

    def loaded(self):
        return self.rom_contents_buffer is not None

    def close(self):
        if self.file_object is not None:
            self.file_object.close()

    def read_compressed(self, address):
        return lz77.decompress(self.rom_contents_buffer[address::])

    def alloc_modified_data(self, data, original_data_size, original_adress,
                            compressed=False, delete_old=False, start_address=0):
        if compressed:
            data = lz77.compress(data)

        if delete_old:
            self.delete_data(original_adress, original_data_size)

        data_size = len(data)
        if data_size > original_data_size:
            new_address = self.write_at_free_space(data, start_address)
        else:
            self.write(original_adress, data)
            new_address = original_adress

        return new_address, data_size

    def read_struct_at(self, address, StructClass):
        struct_obj = StructClass()
        struct_obj.load_from_bytes(self.read(address, StructClass.size()))
        return struct_obj

    def get_map_header_pointer(self, map_index, map_subindex):
        header_data_subtable = self.MAP_HEADER_TABLE + map_index * 4
        return self.read_pointer(header_data_subtable) + map_subindex * MapHeader.size()

    def get_map_layer_header_pointer(self, map_index, map_subindex, layer_num):
        layer_header_subtable = self.read_pointer(self.MAP_LAYER_HEADER_TABLE + map_index * 4)
        layer_header_array_pointer = self.read_pointer(layer_header_subtable + map_subindex * 4)
        return layer_header_array_pointer + layer_num * MapDataGenericHeader.size()

    def get_blocks_header_pointer(self, map_index, blocks_index):
        return self.read_pointer(self.BLOCKS_TABLE + 4 * map_index) + blocks_index * MapDataGenericHeader.size()

    def get_palette_header2_pointer(self, palette_header2_index):
        return self.read_pointer(self.PALETTE_HEADER2_TABLE + palette_header2_index * 4)

    def get_palette_pointer(self, palette_index):
        return self.PALETTE_TABLE + palette_index * 32

    def get_tilesets_and_palette_headers_array_ptr(self, map_index, tileset_index):
        tileset_subtable = self.read_pointer(self.TILESETS_TABLE + map_index * 4)
        return self.read_pointer(tileset_subtable + tileset_index * 4)

    def get_scripts_array_ptr(self, map_index, map_subindex):
        sub_table_ptr = self.read_pointer(self.SCRIPTs_TABLE + map_index * 4)
        return self.read_pointer(sub_table_ptr + map_subindex * 4)

    def get_warps_array_ptr(self, map_index, map_subindex):
        sub_table_ptr = self.read_pointer(self.WARPS_TABLE + map_index * 4)
        return self.read_pointer(sub_table_ptr + map_subindex * 4)
