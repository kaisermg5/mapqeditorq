
MAP_HEADER_TABLE = 0x11e214

TILESETS_TABLE = 0x10246c  # Table of tables
unk_table1 = 0x107988
BLOCKS_TABLE = 0x10309c  # Pointer to pointer table
unk_table2 = 0xb755c
unk_table3 = 0x13a7f0
unk_table4 = 0xd50fc


class Game:
    def __init__(self):
        self.file_object = None
        self.rom_contents = None

    def load(self, filename):
        self.file_object = open(filename, 'rb+')
        self.rom_contents = self.file_object.read()
        if self.rom_contents[0xac:0xb0] != b'BZME':
            # Warning
            return 1
        return 0

    def read_u32(self, address):
        return int.from_bytes(self.rom_contents[address:address+4], 'little')

    def read_pointer(self, address):
        return self.read_u32(address) - 0x8000000
