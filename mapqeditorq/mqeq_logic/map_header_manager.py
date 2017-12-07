
import os
from .parsers import hex_format, CDefinition, AsmParser
from ..maps.maps import MapHeader, InvalidMap
from . import common
from . import file_utils
from . data_structure_bases import NumberTableBase, StructTableBase


class MapHeaderMainTable(NumberTableBase):
    def extract_array(self, game):
        return game.get_map_header_array()


class MapHeaderGroupTable(StructTableBase):
    StructClass = MapHeader

    def __init__(self, group, filename, definition):
        super().__init__(filename, definition)
        self.group = group
        self.definition.format_label(hex_format(group))

    def extract_array(self, game):
        return game.get_map_header_array(self.group)


class MapHeaderManager:
    MAIN_TABLE_FILENAME = 'main_headers_table.c'
    MAIN_TABLE_DEFINITION = CDefinition(
        'const struct MapHeader',
        'map_header_table',
        base_format='( * {0} [ ] ) [ ]'
    )

    GROUP_TABLE_FILENAME = 'headers_table.c'

    def __init__(self):
        self.main_table = MapHeaderMainTable(
            self.get_main_table_filename(),
            self.get_main_table_definition()
        )
        self.group_table = None

    def get_main_table_definition(self):
        return self.MAIN_TABLE_DEFINITION

    @staticmethod
    def get_group_table_definition(group):
        ret = CDefinition(
            'const struct MapHeader',
            'map_group_{0}_header_table'.format(group),
            base_format='{0} [ ]'
        )
        return ret

    def get_main_table_filename(self):
        return common.resource_path_join(common.MAPS_DIR, self.MAIN_TABLE_FILENAME)

    def get_group_filename(self, group):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.GROUP_TABLE_FILENAME
        )
        return path

    def load_main_table(self, game):
        self.main_table.load(game)
        fn = common.resource_path_join(
            common.ASM_PATCHES_DIR,
            'map_headers_table_repoint.sinc'
        )
        if not os.path.exists(fn):
            with file_utils.EasyOpen(fn, 'w') as f:
                f. write(AsmParser.format_repoints(
                    self.main_table.get_label(), game.PTRS_TO_MAP_HEADER_TABLE
                ))

    def load_group_table(self, game, group):
        self.group_table = MapHeaderGroupTable(
            group,
            self.get_group_filename(group),
            self.get_group_table_definition(group)
        )

        self.group_table.load(game)

        if self.main_table[group] != self.group_table.get_label():
            self.main_table[group] = self.group_table.definition.as_extern()
            self.main_table.save()

    def save_changes(self):
        if self.group_table is not None and self.group_table.was_modified():
            self.group_table.save()

        if self.main_table.was_modified():
            self.main_table.save()

    def discard_changes(self):
        if self.group_table is not None:
            self.group_table = None

        if self.main_table.was_modified():
            self.main_table = None

    def get_map_header(self, game, map_index, map_subindex):
        self.load_main_table(game)

        if map_index >= len(self.main_table):
            raise InvalidMap('There is no map group with index: {0}'.format(map_index))
        elif isinstance(self.main_table[map_index], int):
            ptr = self.main_table[map_index]
            if ptr == 0:
                raise InvalidMap('Group {0} table ptr is set to 0.'.format(map_index))
            elif game.pointer_unmask(ptr) <= 0:
                raise InvalidMap('Group {0} table has an invalid ptr: {1}'.format(map_index, ptr))

        self.load_group_table(game, map_index)
        return self.group_table[map_subindex]

