
from mapqeditorq.game import lz77

from mapqeditorq.maps.maps import MapHeader
from mapqeditorq.maps.common import MapDataGenericHeader


class Game:
    # Game pointers
    MAP_HEADER_TABLE = 0x11e214
    PTRS_TO_MAP_HEADER_TABLE = (
        0x0801dc88,
        0x0801dd50,
        0x0801dd7c,
        0x0801df08,
        0x08052cc8,
        0x08052cf4,
        0x08052df8,
        0x08053078,
        0x08053318,
        0x080a6a40,
        0x080a6f38,
    )


    TILESETS_TABLE = 0x10246c
    PTRS_TO_MAP_TILESETS_TABLE = (
        0x08052e74,
        0x0805307c,
    )

    MAP_LAYER_HEADER_TABLE = 0x107988
    PTRS_TO_MAP_LAYERS_TABLE = (
        0x08052e78,
        0x08053080
    )

    BLOCKS_TABLE = 0x10309c
    PTRS_TO_MAP_BLOCKS_TABLE = (
        0x08052e7c,
        0x08053084
    )

    unk_table2 = 0xb755c

    WARPS_TABLE = 0x13a7f0
    PTRS_TO_MAP_WARPS_TABLE = (
        0x08052e84,
    )

    SCRIPTS_TABLE = 0xd50fc

    PALETTE_HEADER2_TABLE = 0xff850
    PALETTE_TABLE = 0x5a2e80

    unk_table_5 = 0x127d30

    def __init__(self):
        self.rom_contents = None

    def load(self, filename):
        with open(filename, 'rb+') as f:
            self.rom_contents = f.read()
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
        return self.rom_contents[address:address + amount_of_bytes]

    def read_u32(self, address):
        return int.from_bytes(self.read(address, 4), 'little')

    def read_pointer(self, address):
        return self.pointer_unmask(self.read_u32(address))

    def loaded(self):
        return self.rom_contents is not None

    def read_compressed(self, address):
        return lz77.decompress(self.rom_contents[address::])

    def read_struct_at(self, address, StructClass):
        struct_obj = StructClass()
        struct_obj.load_from_bytes(self.read(address, StructClass.size()))
        return struct_obj

    def get_map_header_pointer(self, map_index, map_subindex):
        header_data_subtable = self.MAP_HEADER_TABLE + map_index * 4
        return self.read_pointer(header_data_subtable) + map_subindex * MapHeader.size()

    def get_map_layer_headers_address(self, map_index, map_subindex):
        layer_header_subtable = self.read_pointer(self.MAP_LAYER_HEADER_TABLE + map_index * 4)
        return self.read_pointer(layer_header_subtable + map_subindex * 4)

    def get_map_layer_header_pointer(self, map_index, map_subindex, layer_num):
        layer_header_array_pointer = self.get_map_layer_headers_address(map_index, map_subindex)
        return layer_header_array_pointer + layer_num * MapDataGenericHeader.size()

    def get_blocks_header_pointer(self, map_index):
        return self.read_pointer(self.BLOCKS_TABLE + 4 * map_index)

    def get_palette_header2_pointer(self, palette_header2_index):
        return self.read_pointer(self.PALETTE_HEADER2_TABLE + palette_header2_index * 4)

    def get_palette_pointer(self, palette_index):
        return self.PALETTE_TABLE + palette_index * 32

    def get_tilesets_and_palette_headers_ptr(self, map_index, tileset_index):
        tileset_subtable = self.get_tileset_group_subtable_ptr(map_index)
        return self.read_pointer(tileset_subtable + tileset_index * 4)

    def get_tileset_group_subtable_ptr(self, map_index):
        return self.read_pointer(self.TILESETS_TABLE + map_index * 4)

    def get_scripts_array_ptr(self, map_index, map_subindex):
        sub_table_ptr = self.read_pointer(self.SCRIPTS_TABLE + map_index * 4)
        return self.read_pointer(sub_table_ptr + map_subindex * 4)

    def get_warps_array_ptr(self, map_index, map_subindex):
        sub_table_ptr = self.read_pointer(self.WARPS_TABLE + map_index * 4)
        return self.read_pointer(sub_table_ptr + map_subindex * 4)

    def read_u32_array(self, address, length):
        array = []
        for i in range(length):
            array.append(self.read_u32(address))
            address += 4
        return array

    def read_struct_array(self, address, length, StructClass):
        array = []
        for i in range(length):
            array.append(self.read_struct_at(address, StructClass))
            address += StructClass.size()
        return array

    def get_map_groups_quanty(self):
        # FIXME: check the actual quantity
        return 0x80

    def get_map_group_length(self, group):
        # FIXME: check the actual quantity
        return 0x80

    def get_map_header_array(self, group=None):
        address = self.MAP_HEADER_TABLE
        if group is not None:
            address += 4 * group
            address = self.read_pointer(address)
            array = self.read_struct_array(address, self.get_map_group_length(group), MapHeader)
        else:
            array = self.read_u32_array(address, self.get_map_groups_quanty())
        return array

    def read_mapdata_main_table(self, address):
        return self.read_u32_array(address, self.get_map_groups_quanty())

    def read_mapdata_group_table(self, table_address, group):
        address = self.read_pointer(table_address + 4 * group)
        return self.read_u32_array(address, self.get_map_groups_quanty())

    def get_map_layer_array(self, group=None):
        if group is None:
            return self.read_mapdata_main_table(self.MAP_LAYER_HEADER_TABLE)
        else:
            return self.read_mapdata_group_table(self.MAP_LAYER_HEADER_TABLE, group)

    def get_map_blocks_array(self):
        return self.read_mapdata_main_table(self.BLOCKS_TABLE)

    def get_map_tilesets_array(self):
        return self.read_mapdata_main_table(self.TILESETS_TABLE)

    def get_map_warps_array(self, group=None):
        if group is None:
            return self.read_mapdata_main_table(self.WARPS_TABLE)
        else:
            return self.read_mapdata_group_table(self.WARPS_TABLE, group)

    def get_mapdata_generic_header_array(self, address):
        array = []
        while True:
            header = self.read_struct_at(address, MapDataGenericHeader)
            array.append(header)
            if header.is_final():
                break
            address += MapDataGenericHeader.size()
        return array
