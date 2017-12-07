
import os
import pickle

from . import common


class UserSettings:
    def __init__(self):
        self.last_opened_path = '.'

    @classmethod
    def load(cls):
        if os.path.exists(common.SETTINGS_FILENAME):
            with open(common.SETTINGS_FILENAME, 'rb') as f:
                settings = pickle.load(f)
            if not isinstance(settings, cls):
                settings = cls()
        else:
            settings = cls()
        return settings

    def save(self):
        with open(common.SETTINGS_FILENAME, 'wb') as f:
            pickle.dump(self, f)
