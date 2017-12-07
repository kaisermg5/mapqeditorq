
import os
import sys
from . import file_utils
from .parsers import hex_format
from .data_structure_bases import IncludedBinaryFileBase

MAPS_DIR = 'data/maps'
ASM_PATCHES_DIR = 'asm/mqeq/patches'
EDITOR_DIRECTORY = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])))
TMP_DIR = os.path.join(EDITOR_DIRECTORY, 'tmp')
SETTINGS_FILENAME = os.path.join(EDITOR_DIRECTORY, 'settings.dat')

TILESET_MAX_SIZE = 512


class MqeqError(Exception):
    pass


def get_temp_dir():
    if not os.path.exists(TMP_DIR):
        file_utils.mkdirs_p(TMP_DIR)
    return TMP_DIR


MAP_FILES_INCLUDES = '\n#include <global.h>\n#include <map.h>\n\n'


def resource_path_join(path_left, path_rigth):
    return path_left + '/' + path_rigth


def get_group_dir(map_index):
    return resource_path_join(MAPS_DIR, 'group_{0}'.format(hex_format(map_index)))


def get_map_dir(map_index, map_subindex):
    path = resource_path_join(
        get_group_dir(map_index),
        'map_{0}'.format(hex_format(map_subindex))
    )
    return path


class MapDataBinaryFile(IncludedBinaryFileBase):
    def extract_data(self, game):
        address = self.assignd_object.header.get_compressed_data_ptr()
        data, _ = game.read_compressed(address)
        return data

    def set_data_to_object(self, data):
        self.assignd_object.set_data(data)

    def was_modified(self):
        return self.assignd_object.was_modified()

    def after_saving_object_update(self):
        if isinstance(self.assignd_object.header.get_compressed_data_ptr(), int):
            label = '&' + self.definition.get_label()
            self.assignd_object.header.set_compressed_data_ptr(label)
            self.assignd_object.header.add_dependency(self.definition)
        self.assignd_object.set_modified(False)

    def get_data_from_object(self):
        return self.assignd_object.to_bytes()

