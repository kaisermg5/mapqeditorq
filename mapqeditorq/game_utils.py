
MAP_HEADER_TABLE = 0x11e214

TILESETS_TABLE = 0x10246c  # Table of tables
MAPDATA_TABLE = 0x107988
BLOCKS_TABLE = 0x10309c  # Pointer to pointer table
unk_table2 = 0xb755c
unk_table3 = 0x13a7f0
unk_table4 = 0xd50fc

PALETTE_HEADER_TABLE = 0xff850
PALETTE_TABLE = 0x5a2e80


class Game:
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

    def read(self, address, amount_of_bytes):
        return self.rom_contents_buffer[address:address + amount_of_bytes]

    def read_u32(self, address):
        return int.from_bytes(self.read(address, 4), 'little')

    def read_pointer(self, address):
        return self.read_u32(address) - 0x8000000

    def find_free_space(self, size, start_address=0):
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


