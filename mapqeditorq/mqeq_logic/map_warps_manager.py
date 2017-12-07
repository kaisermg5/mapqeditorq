
from . import common
from . import file_utils
from .parsers import CDefinition, hex_format, AsmParser
from .data_structure_bases import NumberTableBase, StructTableBase
from ..maps.warps import MapWarp


import os


class MapWarpsMainTable(NumberTableBase):
    def extract_array(self, game):
        return game.get_map_warps_array()


class MapWarpsGroupTable(NumberTableBase):
    def __init__(self, group, filename, definition):
        super().__init__(filename, definition)
        self.group = group

    def extract_array(self, game):
        return game.get_map_warps_array(self.group)


class SpecificMapWarpsTable(StructTableBase):
    StructClass = MapWarp

    def __init__(self, map_index, map_subindex, filename, definition):
        super().__init__(filename, definition)
        self.map_index = map_index
        self.map_subindex = map_subindex

    def extract_array(self, game):
        array = []
        address = game.get_warps_array_ptr(self.map_index, self.map_subindex)
        while True:
            warps_struct = game.read_struct_at(address, MapWarp)
            array.append(warps_struct)
            if warps_struct.unk_0 == 0xFFFF:
                break
            address += MapWarp.size()
        return array


class MapWarpsManager:
    MAIN_TABLE_FILENAME = 'warps_main_table.c'
    MAIN_TABLE_DEFINITION = CDefinition(
        'const struct MapWarp',
        'map_warps_main_table',
        base_format='( * ( * {0} [ ] ) [ ] ) [ ]'
    )

    GROUP_TABLE_FILENAME = 'warps_table.c'

    SPECIFIC_MAP_FILENAME = 'warps.c'

    def __init__(self):
        self.main_table = MapWarpsMainTable(
            self.get_main_table_filename(),
            self.MAIN_TABLE_DEFINITION
        )
        self.group_table = None

        self.loaded_map_warps_table = None

    @staticmethod
    def get_group_table_definition(group):
        definition = CDefinition(
            'const struct MapWarp',
            'map_warps_group_{0}_table'.format(hex_format(group)),
            base_format='( * {0} [ ] ) [ ]'
        )
        return definition

    @staticmethod
    def get_map_warps_definition(map_index, map_subindex):
        definition = CDefinition(
            'const struct MapWarp',
            'map_{0}_{1}_warps_table'.format(hex_format(map_index), hex_format(map_subindex)),
            base_format='{0} [ ]'
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

    def get_specific_map_filename(self, map_index, map_subindex):
        path = common.resource_path_join(
            common.get_map_dir(map_index, map_subindex),
            self.SPECIFIC_MAP_FILENAME
        )
        return path

    def load_main_table(self, game):
        self.main_table.load(game)
        fn = common.resource_path_join(
            common.ASM_PATCHES_DIR,
            'map_warps_table_repoint.sinc'
        )
        if not os.path.exists(fn):
            with file_utils.EasyOpen(fn, 'w') as f:
                f.write(AsmParser.format_repoints(
                    self.main_table.get_label(), game.PTRS_TO_MAP_WARPS_TABLE
                ))

    def load_group_table(self, game, group):
        if not self.main_table.loaded():
            self.load_main_table(game)

        self.group_table = MapWarpsGroupTable(
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

        self.loaded_map_warps_table = SpecificMapWarpsTable(
            map_index,
            map_subindex,
            self.get_specific_map_filename(map_index, map_subindex),
            self.get_map_warps_definition(map_index, map_subindex)
        )
        self.loaded_map_warps_table.load(game)

        if self.group_table[map_subindex] != self.loaded_map_warps_table.get_label():
            self.group_table[map_subindex] = self.loaded_map_warps_table.definition.as_extern()
            self.group_table.save()

    def get_warps(self, game, map_index, map_subindex):
        self.load_headers_table(game, map_index, map_subindex)
        return self.loaded_map_warps_table.get_array()

    def save_changes(self):
        if self.loaded_map_warps_table is not None and \
                self.loaded_map_warps_table.was_modified():
            self.loaded_map_warps_table.save()

        if self.group_table is not None and self.group_table.was_modified():
            self.group_table.save()

        if self.main_table.was_modified():
            self.main_table.save()

    def discard_changes(self):
        if self.main_table.was_modified():
            self.main_table.discard_changes()
        if self.group_table is not None:
            self.group_table = None
        if self.loaded_map_warps_table is not None:
            self.loaded_map_warps_table = None






