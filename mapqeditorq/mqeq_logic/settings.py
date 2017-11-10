
import os
import sys
import pickle

EDITOR_DIRECTORY = os.path.dirname(os.path.realpath(sys.argv[0]))
SETTINGS_FILENAME = os.path.join(EDITOR_DIRECTORY, 'settings.dat')


class UserSettings:
    def __init__(self):
        self.last_opened_path = '.'

    @classmethod
    def load(cls):
        if os.path.exists(SETTINGS_FILENAME):
            with open(SETTINGS_FILENAME, 'rb') as f:
                settings = pickle.load(f)
            if not isinstance(settings, cls):
                settings = cls()
        else:
            settings = cls()
        return settings

    def save(self):
        with open(SETTINGS_FILENAME, 'wb') as f:
            pickle.dump(self, f)
