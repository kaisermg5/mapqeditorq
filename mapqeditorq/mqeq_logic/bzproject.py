
from ..game.game import Game
from ..maps.maps import Map
from . import common
from .map_header_manager import MapHeaderManager
from .map_layer_manager import MapLayerManager
from .map_blocks_manager import MapBlocksManager
from .map_tileset_and_palettes_manager import MapTilesetAndPalettesManager
from .map_warps_manager import MapWarpsManager

import shutil
import configparser
import os

PROJECT_BASE = os.path.join(common.EDITOR_DIRECTORY, 'projectbase')


class BzProj:
    BASEROM_NAME = 'baserom.gba'

    def __init__(self):
        self.game = Game()
        self.config = configparser.ConfigParser()
        self.project_filename = None

        self.map_header_manager = MapHeaderManager()
        self.map_layers_manager = MapLayerManager()
        self.map_blocks_manager = MapBlocksManager()
        self.map_tilesets_and_palettes_manager = MapTilesetAndPalettesManager()
        self.map_warps_manager = MapWarpsManager()

    def create(self, rom_filename, project_dir, project_name):
        project_dir = os.path.join(project_dir, project_name)
        if not os.path.exists(rom_filename):
            raise common.MqeqError('The rom "{0}" does not exist.'.format(rom_filename))
        try:
            shutil.copytree(PROJECT_BASE, project_dir)
        except FileExistsError:
            raise common.MqeqError(
                'Cannot create project with name "{0}". A directory with that name already '
                'exists in the specified project\'s directory.'.format(project_name)
            )
        shutil.copyfile(rom_filename, os.path.join(project_dir, self.BASEROM_NAME))

        self.project_filename = os.path.join(project_dir, project_name + '.bzproj')
        self.config['PROJECT'] = {
            'Rom': self.BASEROM_NAME,
            'ProjectVersion': str(1),
        }
        self.config['MQEQ'] = {

        }
        self.save_config()
        os.chdir(project_dir)
        self.game.load(self.BASEROM_NAME)

    def load(self, proj_filename):
        self.project_filename = os.path.abspath(proj_filename)
        self.config.read(self.project_filename)
        os.chdir(os.path.dirname(self.project_filename))
        self.game.load(self.config['PROJECT']['Rom'])

    def close(self):
        self.save_config()

    def save_config(self):
        with open(self.project_filename, 'w') as f:
            self.config.write(f)

    def load_map(self, index, subindex):
        map_obj = Map()
        map_obj.load(index, subindex, self)
        return map_obj

    def get_map_header(self, map_index, map_subindex):
        return self.map_header_manager.get_map_header(self.game, map_index, map_subindex)

    def get_map_layers(self, map_index, map_subindex):
        return self.map_layers_manager.get_layers(self.game, map_index, map_subindex)

    def get_map_blocks(self, map_index):
        return self.map_blocks_manager.get_blocks(self.game, map_index)

    def get_tileset_load_palettes(self, map_index, tilesets_index, palettes_obj):
        tilesets = self.map_tilesets_and_palettes_manager.get_tilesets_load_palettes(
            self.game, map_index, tilesets_index, palettes_obj
        )
        return tilesets

    def get_warps(self, map_index, map_subindex):
        self.map_warps_manager.get_warps(self.game, map_index, map_subindex)

    def save_changes(self):
        self.map_layers_manager.save_changes()
        self.map_blocks_manager.save_changes()
        self.map_header_manager.save_changes()
        self.map_tilesets_and_palettes_manager.save_changes()
        self.map_warps_manager.save_changes()





