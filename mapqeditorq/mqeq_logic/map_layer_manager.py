
from . import common
from . import file_utils
from .parsers import CDefinition, hex_format, AsmParser
from .data_structure_bases import NumberTableBase, StructTableBase
from ..maps.common import MapDataGenericHeader
from ..maps.map_layer import MapLayer


import os


class MapLayersMainTable(NumberTableBase):
    def extract_array(self, game):
        return game.get_map_layer_array()


class MapLayersGroupTable(NumberTableBase):
    def __init__(self, group, filename, definition):
        super().__init__(filename, definition)
        self.group = group

    def extract_array(self, game):
        return game.get_map_layer_array(self.group)


class MapLayerHeadersTable(StructTableBase):
    StructClass = MapDataGenericHeader

    def __init__(self, map_index, map_subindex, filename, definition):
        super().__init__(filename, definition)
        self.map_index = map_index
        self.map_subindex = map_subindex

    def extract_array(self, game):
        address = game.get_map_layer_headers_address(self.map_index, self.map_subindex)
        return game.get_mapdata_generic_header_array(address)


class MapLayerManager:
    MAIN_TABLE_FILENAME = 'layers_main_table.c'
    MAIN_TABLE_DEFINITION = CDefinition(
        'const struct MapDataGenericHeader',
        'map_layers_main_table',
        base_format='( * ( * {0} [ ] ) [ ] ) [ ]'
    )

    GROUP_TABLE_FILENAME = 'layers_table.c'

    SPECIFIC_MAP_FILENAME = 'map_{0}_{1}_data.c'
    LAYER_FILENAME = 'layer_{0}.bin'

    LAYER_INDEXES = {
        MapDataGenericHeader.MAP_LAYER_1: 0,
        MapDataGenericHeader.MAP_LAYER_2: 1
    }

    def __init__(self):
        self.main_table = MapLayersMainTable(
            self.get_main_table_filename(),
            self.MAIN_TABLE_DEFINITION
        )
        self.group_table = None

        self.loaded_map_headers_table = None
        self.loaded_incbins = None

    @staticmethod
    def get_group_table_definition(group):
        definition = CDefinition(
            'const struct MapDataGenericHeader',
            'map_layers_group_{0}_table'.format(hex_format(group)),
            base_format='( * {0} [ ] ) [ ]'
        )
        return definition

    @staticmethod
    def get_headers_definition(map_index, map_subindex):
        definition = CDefinition(
            'const struct MapDataGenericHeader',
            'map_{0}_{1}_layers_table'.format(hex_format(map_index), hex_format(map_subindex)),
            base_format='{0} [ ]'
        )
        return definition

    @staticmethod
    def get_map_layer_incbin_definition(layer_num):
        definition = CDefinition(
            'const u8',
            'map_layer_data_{0}'.format(layer_num),
            base_format='{0} [ ]',
            visibility=CDefinition.STATIC
        )
        return definition

    def get_main_table_filename(self):
        return common.resource_path_join(common.MAPS_DIR, self.MAIN_TABLE_FILENAME)

    def get_group_table_filename(self, group):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.GROUP_TABLE_FILENAME
        )
        return path

    def get_headers_filename(self, map_index, map_subindex):
        path = common.resource_path_join(
            common.get_map_dir(map_index, map_subindex),
            self.SPECIFIC_MAP_FILENAME.format(hex_format(map_index), hex_format(map_subindex))
        )
        return path

    def get_layer_filename(self, map_index, map_subindex, layer_num):
        path = os.path.join(
            common.get_map_dir(map_index, map_subindex),
            self.LAYER_FILENAME.format(layer_num)
        )
        return path

    def load_main_table(self, game):
        self.main_table.load(game)
        fn = common.resource_path_join(
            common.ASM_PATCHES_DIR,
            'map_layers_table_repoint.sinc'
        )
        if not os.path.exists(fn):
            with file_utils.EasyOpen(fn, 'w') as f:
                f.write(AsmParser.format_repoints(
                    self.main_table.get_label(), game.PTRS_TO_MAP_LAYERS_TABLE
                ))

    def load_group_table(self, game, group):
        if not self.main_table.loaded():
            self.load_main_table(game)

        self.group_table = MapLayersGroupTable(
                group,
                self.get_group_table_filename(group),
                self.get_group_table_definition(group)
            )

        self.group_table.load(game)

        if self.main_table[group] != self.group_table.get_label():
            self.main_table[group] = self.group_table.definition.as_extern()
            self.main_table.save()

    def load_headers_table(self, game, map_index, map_subindex):
        if self.group_table is None:
            self.load_group_table(game, map_index)

        self.loaded_map_headers_table = MapLayerHeadersTable(
            map_index,
            map_subindex,
            self.get_headers_filename(map_index, map_subindex),
            self.get_headers_definition(map_index, map_subindex)
        )
        self.loaded_map_headers_table.load(game)

        if self.group_table[map_subindex] != self.loaded_map_headers_table.get_label():
            self.group_table[map_subindex] = self.loaded_map_headers_table.definition.as_extern()
            self.group_table.save()

    def get_layers(self, game, map_index, map_subindex):
        self.load_headers_table(game, map_index, map_subindex)

        map_layers = [MapLayer(), MapLayer()]
        self.loaded_incbins = [None, None]
        for i in range(len(self.loaded_map_headers_table)):
            header = self.loaded_map_headers_table[i]

            layer_num = self.get_layer_num(header)
            if layer_num is not None:
                map_layers[layer_num].set_header(header)
                self.loaded_incbins[layer_num] = common.MapDataBinaryFile(
                    self.get_layer_filename(map_index, map_subindex, layer_num),
                    self.get_headers_filename(map_index, map_subindex),
                    self.get_map_layer_incbin_definition(layer_num),
                    map_layers[layer_num]
                )
                self.loaded_incbins[layer_num].load_data(game)

        return map_layers

    def get_layer_num(self, header):
        layer_num = None
        header_type = header.header_type()

        # TODO: find out what the other data is...
        # check map 0x3, 0x1
        if header_type == MapDataGenericHeader.UNSPECTED_STR_TYPE \
                and header.uncompress_address in self.LAYER_INDEXES:
            layer_num = self.LAYER_INDEXES[header.uncompress_address]
        elif header_type in self.LAYER_INDEXES:
            layer_num = self.LAYER_INDEXES[header_type]
        return layer_num

    def save_changes(self):
        if self.loaded_incbins is not None:
            for incbin in self.loaded_incbins:
                if incbin is not None and incbin.was_modified():
                    incbin.save()

        if self.loaded_map_headers_table is not None and \
                self.loaded_map_headers_table.was_modified():
            self.loaded_map_headers_table.save()

        if self.group_table is not None and self.group_table.was_modified():
            self.group_table.save()

        if self.main_table.was_modified():
            self.main_table.save()

    def discard_changes(self):
        if self.main_table.was_modified():
            self.main_table.discard_changes()
        if self.group_table is not None:
            self.group_table = None
        if self.loaded_map_headers_table is not None:
            self.loaded_map_headers_table = None
        if self.loaded_incbins is not None:
            self.loaded_incbins = None






