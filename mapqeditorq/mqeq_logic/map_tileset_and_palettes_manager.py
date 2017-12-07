
from . import common
from . import file_utils
from .parsers import CDefinition, hex_format, CParser, AsmParser, \
    convert_16_color_palette_to_pal_file_format, get_16_color_palette_from_pal_file_format
from .data_structure_bases import NumberTableBase, StructTableBase
from ..maps.common import MapDataGenericHeader
from ..maps.tilesets import Tileset


import os
from PIL import Image


class MapTilesetsMainTable(NumberTableBase):
    def extract_array(self, game):
        return game.get_map_tilesets_array()


class GroupTilesetTable(NumberTableBase):
    def __init__(self, group, filename, definition):
        super().__init__(filename, definition)
        self.group = group

    def extract_array(self, game):
        address = game.get_tileset_group_subtable_ptr(self.group)
        return game.read_u32_array(address, 4)


class GroupTilesetsHeadersTable(StructTableBase):
    StructClass = MapDataGenericHeader

    def __init__(self, tilesets_index, group, filename, definition):
        super().__init__(filename, definition)
        self.tilesets_index = tilesets_index
        self.group = group

    def extract_array(self, game):
        address = game.get_tilesets_and_palette_headers_ptr(self.group, self.tilesets_index)
        return game.get_mapdata_generic_header_array(address)


class TilesetIncBinManager:
    def __init__(self, img_filename, definition_filename, definition, tileset_obj):
        self.img_filename = img_filename
        self.definition_filename = definition_filename
        self.definition = definition
        self.tileset_obj = tileset_obj

    def load(self, game):
        if os.path.exists(self.img_filename):
            img = Image.open(self.img_filename)
            self.tileset_obj.set_image(img)
        else:
            if not isinstance(self.tileset_obj.header.get_compressed_data_ptr(), int):
                raise Exception('Tileset image was deleted')
            self.tileset_obj.load_from_game(game)

    def was_modified(self):
        return self.tileset_obj.was_modified()

    def save(self):
        img = self.tileset_obj.get_full_tileset(0)
        w, h = img.size
        img = img.resize((w // 2, h // 2))
        img.save(self.img_filename, 'PNG')

        with file_utils.TextFileEditor(
                self.definition_filename,
                file_header=common.MAP_FILES_INCLUDES) as f:
            txt = f.read_contents()
            new_txt = self.get_initialization_text()
            if not CParser.is_definition_in_text(self.definition, txt):
                txt = CParser.change_initialization(
                    txt, self.definition, new_txt
                )
                f.write(txt)
            else:
                f.cancel()
        self.tileset_obj.modified = False

        if isinstance(self.tileset_obj.header.get_compressed_data_ptr(), int):
            label = '&' + self.definition.get_label()
            self.tileset_obj.header.set_compressed_data_ptr(label)
            self.tileset_obj.header.add_dependency(self.definition)

    def get_initialization_text(self):
        filename = self.img_filename.replace('.png', '.4bpp.lz')
        filename = common.resource_path_join('build/build', filename)
        return CParser.format_incbin(self.definition, filename)


class PalettesIncBinManager:
    def __init__(self, pal_base_filename, definition_filename, definition, pal_obj):
        self.pal_base_filename = pal_base_filename
        self.definition_filename = definition_filename
        self.definition = definition
        self.pal_obj = pal_obj

    def load(self, game):
        self.pal_obj.load_shared_palettes(game)
        filename = self.pal_base_filename.format(2)
        if os.path.exists(filename):
            palettes = [None] * 13
            for i in range(13):
                filename = self.pal_base_filename.format(i + 2)
                with open(filename, newline='\r\n') as f:
                    contents = f.read()
                palettes[i] = get_16_color_palette_from_pal_file_format(contents)
            self.pal_obj.set_palettes(palettes)
        else:
            self.pal_obj.extract_from_game(game)

    def was_modified(self):
        return self.pal_obj.was_modified()

    def save(self):
        for i in range(2, 15):
            filename = self.pal_base_filename.format(i)
            palette = self.pal_obj.palettes_list[i]
            pal_data = convert_16_color_palette_to_pal_file_format(palette)
            with file_utils.EasyOpen(filename, 'w', newline='\r\n') as f:
                f.write(pal_data)

        with file_utils.TextFileEditor(
                self.definition_filename,
                file_header=common.MAP_FILES_INCLUDES) as f:
            txt = f.read_contents()
            if not CParser.is_definition_in_text(self.definition, txt):
                initialization = self.get_initialization_text()
                txt = CParser.change_initialization(
                    txt, self.definition, initialization
                )
                f.write(txt)
            else:
                f.cancel()
        if isinstance(self.pal_obj.header1.masked_data_ptr, int):
            self.pal_obj.header1.set_palettes_ptr('&' + self.definition.get_label())
            self.pal_obj.header1.add_dependency(self.definition)
        self.pal_obj.modified = False

    def get_initialization_text(self):
        filenames = []
        for i in range(2, 15):
            filename = common.resource_path_join('build', self.pal_base_filename.format(i))
            filename = filename.replace('.pal', '.gbapal')
            filenames.append(filename)
        return CParser.format_incbin_array(self.definition, filenames)


class MapTilesetAndPalettesManager:
    MAIN_TABLE_FILENAME = 'tilesets_main_table.c'
    MAIN_TABLE_DEFINITION = CDefinition(
        'const struct MapDataGenericHeader',
        'map_tileset_main_table',
        base_format='( * ( * {0} [ ] ) [ ] ) [ ]'
    )

    SPECIFIC_GROUP_FILENAME = 'tilesets_data.c'
    TILESET_FILENAME = 'tileset_{0}_{1}.png'
    PALETTE_FILENAME = 'palette_{0}_{1}.pal'

    TILESET_IDNTIFIER = {
            MapDataGenericHeader.TILESET_1: 0,
            MapDataGenericHeader.TILESET_2: 1,
            MapDataGenericHeader.TILESET_3: 2,
        }

    def __init__(self):
        self.main_table = MapTilesetsMainTable(
            self.get_main_table_filename(),
            self.MAIN_TABLE_DEFINITION
        )
        self.group_tileset_table = None
        self.loaded_headers_table = None
        self.loaded_incbins = None

    @staticmethod
    def get_group_header_table_definition(tilesets_index):
        definition = CDefinition(
            'const struct MapDataGenericHeader',
            'map_tilesets_headers_table_{0}'.format(tilesets_index),
            '{0} [ ]',
            visibility=CDefinition.STATIC
        )
        return definition

    @staticmethod
    def get_group_tileset_table_definition(group):
        definition = CDefinition(
            'const struct MapDataGenericHeader',
            'map_tilesets_group_{0}_table'.format(hex_format(group)),
            base_format='( * {0} [ ] ) [ ]'
        )
        return definition

    @staticmethod
    def get_tileset_incbin_definition(tilesets_index, tileset_number):
        definition = CDefinition(
            'const u8',
            'tileset_{0}_{1}'.format(tileset_number + 1, tilesets_index),
            base_format='{0} [ ]',
            visibility=CDefinition.STATIC
        )
        return definition

    @staticmethod
    def get_palette_incbin_definition(tilesets_index):
        definition = CDefinition(
            'const u8',
            'palettes_{0}'.format(tilesets_index),
            '{0} [ ] [ 32 ]',
            visibility=CDefinition.STATIC
        )
        return definition

    def get_main_table_filename(self):
        path = os.path.join(
            common.MAPS_DIR,
            self.MAIN_TABLE_FILENAME
        )
        return path

    def get_group_filename(self, group):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.SPECIFIC_GROUP_FILENAME
        )
        return path

    def get_tileset_incbin_filename(self, group, tilesets_index, tileset_num):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.TILESET_FILENAME.format(tileset_num + 1, tilesets_index)
        )
        return path

    def get_palette_incbin_base_filename(self, group, tilesets_index):
        path = common.resource_path_join(
            common.get_group_dir(group),
            self.PALETTE_FILENAME.format('{0}', tilesets_index)
        )
        return path

    def load_main_table(self, game):
        self.main_table.load(game)
        fn = common.resource_path_join(
            common.ASM_PATCHES_DIR,
            'map_tilesets_and_palettes_table_repoint.sinc'
        )
        if not os.path.exists(fn):
            with file_utils.EasyOpen(fn, 'w') as f:
                f.write(AsmParser.format_repoints(
                    self.main_table.get_label(), game.PTRS_TO_MAP_TILESETS_TABLE
                ))

    def load_tables(self, game, group, tilesets_index):
        if not self.main_table.loaded():
            self.load_main_table(game)
        self.group_tileset_table = GroupTilesetTable(
            group,
            self.get_group_filename(group),
            self.get_group_tileset_table_definition(group)
        )
        self.group_tileset_table.load(game)

        if self.main_table[group] != self.group_tileset_table.get_label():
            self.main_table[group] = self.group_tileset_table.definition.as_extern()
            self.main_table.save()

        self.loaded_headers_table = GroupTilesetsHeadersTable(
                tilesets_index,
                group,
                self.get_group_filename(group),
                self.get_group_header_table_definition(tilesets_index)
        )
        self.loaded_headers_table.load(game)

        if self.group_tileset_table[tilesets_index] \
                != self.loaded_headers_table.get_label():
            self.group_tileset_table[tilesets_index] \
                = self.loaded_headers_table.definition.copy()
            self.group_tileset_table.save()

    def get_tileset_num(self, header):
        header_type = header.header_type()
        if header_type in self.TILESET_IDNTIFIER:
            return self.TILESET_IDNTIFIER[header_type]
        print('Unknown decompress address: {}'.format(hex(header.uncompress_address)))
        return None

    def get_tilesets_load_palettes(self, game, map_index, tilesets_index, palettes_obj):
        self.load_tables(game, map_index, tilesets_index)

        tilesets = [Tileset(), Tileset(), Tileset()]
        self.loaded_incbins = [
            None, None, None,
            PalettesIncBinManager(
                self.get_palette_incbin_base_filename(map_index, tilesets_index),
                self.get_group_filename(map_index),
                self.get_palette_incbin_definition(tilesets_index),
                palettes_obj
            )
        ]
        for header in self.loaded_headers_table:
            if not header.is_palette_header():
                tileset_num = self.get_tileset_num(header)
                if tileset_num is None:
                    continue
                tilesets[tileset_num].set_header(header)
                tilesets[tileset_num].set_palettes(palettes_obj)
                self.loaded_incbins[tileset_num] = TilesetIncBinManager(
                    self.get_tileset_incbin_filename(map_index, tilesets_index, tileset_num),
                    self.get_group_filename(map_index),
                    self.get_tileset_incbin_definition(tileset_num, tilesets_index),
                    tilesets[tileset_num]
                )
            else:
                palettes_obj.set_header(header)
                self.loaded_incbins[3].load(game)

        for i in range(3):
            self.loaded_incbins[i].load(game)

        return tilesets

    def save_changes(self):
        if self.loaded_incbins is not None:
            for incbin in self.loaded_incbins:
                if incbin.was_modified():
                    incbin.save()

        if self.loaded_headers_table is not None and self.loaded_headers_table.was_modified():
            self.loaded_headers_table.save()

        if self.group_tileset_table is not None and self.group_tileset_table.was_modified():
            self.group_tileset_table.save()

        if self.main_table.was_modified():
            self.main_table.save()

    def discard_changes(self):
        if self.main_table.was_modified():
            self.main_table.discard_changes()

        if self.loaded_incbins is not None:
            self.loaded_incbins = None

        if self.loaded_headers_table is not None:
            self.loaded_headers_table = None

        if self.group_tileset_table is not None:
            self.group_tileset_table = None

