
from . import common
from . import file_utils
from .parsers import CDefinition, hex_format, AsmParser
from .data_structure_bases import NumberTableBase, StructTableBase
from ..maps.common import MapDataGenericHeader
from ..maps.blocks import Blocks


import os


class MapBlocksMainTable(NumberTableBase):
    def extract_array(self, game):
        return game.get_map_blocks_array()


class GroupBlocksHeadersTable(StructTableBase):
    StructClass = MapDataGenericHeader

    def __init__(self, group, filename, definition):
        super().__init__(filename, definition)
        self.group = group

    def extract_array(self, game):
        address = game.get_blocks_header_pointer(self.group)
        return game.get_mapdata_generic_header_array(address)


class MapBlocksManager:
    MAIN_TABLE_FILENAME = 'blocks_main_table.c'
    MAIN_TABLE_DEFINITION = CDefinition(
        'const struct MapDataGenericHeader',
        'map_blocks_main_table',
        base_format='( * {0} [ ] ) [ ]'
    )

    SPECIFIC_GROUP_FILENAME = 'blocks_data.c'
    BLOCKS_RAW_DATA_FILENAME = 'blocks_{0}_{1}.bin'

    BLOCKS_DATA_IDENTIFIER = {
        # KEY:  (is_block_img_data, layer_num)
        #       if it is not data from the image,
        #       it is data from the behaviours
        MapDataGenericHeader.BLOCKS_1_IMG_DATA: (True, 0),
        MapDataGenericHeader.BLOCKS_2_IMG_DATA: (True, 1),
        MapDataGenericHeader.BLOCKS_1_BEHAVIOURS: (False, 0),
        MapDataGenericHeader.BLOCKS_2_BEHAVIOURS: (False, 1),
    }

    def __init__(self):
        self.main_table = MapBlocksMainTable(
            self.get_main_table_filename(),
            self.MAIN_TABLE_DEFINITION
        )
        self.header_tables = None
        self.loaded_incbins = None

    @staticmethod
    def get_group_table_definition(group):
        definition = CDefinition(
            'const struct MapDataGenericHeader',
            'map_blocks_group_{0}_table'.format(hex_format(group)),
            base_format='{0} [ ]'
        )
        return definition

    @staticmethod
    def get_incbin_definition(blocks_index, is_img_data):
        definition = CDefinition(
            'const u8',
            'blocks_{0}_{1}'.format(blocks_index, ('behaviours', 'data')[is_img_data]),
            '{0} [ ]',
            visibility=CDefinition.STATIC
        )
        return definition

    def get_main_table_filename(self):
        path = os.path.join(
            common.MAPS_DIR,
            self.MAIN_TABLE_FILENAME
        )
        return path

    def get_headers_filename(self, group):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.SPECIFIC_GROUP_FILENAME
        )
        return path

    def get_incbin_filename(self, group, blocks_index, is_img_data):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.BLOCKS_RAW_DATA_FILENAME.format(blocks_index, ('behaviours', 'data')[is_img_data])
        )
        return path

    def load_main_table(self, game):
        self.main_table.load(game)
        fn = common.resource_path_join(
            common.ASM_PATCHES_DIR,
            'map_blocks_table_repoint.sinc'
        )
        if not os.path.exists(fn):
            with file_utils.EasyOpen(fn, 'w') as f:
                f.write(AsmParser.format_repoints(
                    self.main_table.get_label(), game.PTRS_TO_MAP_BLOCKS_TABLE
                ))

    def load_group_table(self, game, group):
        if self.header_tables is None:
            self.load_main_table(game)

        self.header_tables = GroupBlocksHeadersTable(
            group,
            self.get_headers_filename(group),
            self.get_group_table_definition(group)
        )
        self.header_tables.load(game)

        if self.main_table[group] != self.header_tables.get_label():
            self.main_table[group] = self.header_tables.definition.as_extern()
            self.main_table.save()

    @classmethod
    def identify_blocks_data_type(cls, header):
        header_type = header.header_type()
        if header_type in cls.BLOCKS_DATA_IDENTIFIER:
            return cls.BLOCKS_DATA_IDENTIFIER[header_type]
        else:
            return None, None

    def get_blocks(self, game, map_index):
        self.load_group_table(game, map_index)

        blocks = [Blocks(), Blocks()]
        self.loaded_incbins = [[None, None], [None, None]]
        for i in range(len(self.header_tables)):
            header = self.header_tables[i]

            is_img_data, blocks_index = self.identify_blocks_data_type(header)
            if blocks_index is not None:
                if is_img_data:
                    obj = blocks[blocks_index]
                else:
                    obj = blocks[blocks_index].get_behaviours_object()
                obj.set_header(header)

                self.loaded_incbins[blocks_index][is_img_data] = common.MapDataBinaryFile(
                    self.get_incbin_filename(map_index, blocks_index, is_img_data),
                    self.get_headers_filename(map_index),
                    self.get_incbin_definition(blocks_index, is_img_data),
                    obj
                )
                self.loaded_incbins[blocks_index][is_img_data].load_data(game)

        return blocks

    def save_changes(self):
        if self.loaded_incbins is not None:
            for it in self.loaded_incbins:
                for incbin in it:
                    if incbin.was_modified():
                        incbin.save()

        if self.header_tables is not None and self.header_tables.was_modified():
            self.header_tables.save()

        if self.main_table.was_modified():
            self.main_table.save()

    def discard_changes(self):
        if self.main_table.was_modified():
            self.main_table.discard_changes()
        if self.header_tables is not None:
            self.header_tables = None
        if self.loaded_incbins is not None:
            self.loaded_incbins = None







