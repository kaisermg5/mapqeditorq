
import os

from . import common


def mkdirs_p(*dirnames):
    for dirname in dirnames:
        if not os.path.exists(dirname):
            os.makedirs(dirname)


def create_containing_dir_if_necessary(filename):
    dirname = os.path.dirname(filename)
    mkdirs_p(dirname)


class EasyOpen:
    def __init__(self, filename, mode='r', file_header=None, **kwargs):
        dir_name = os.path.dirname(filename)
        mkdirs_p(dir_name)
        if 'r' in mode and not os.path.exists(filename):
            creation_mode = ('wb', 'w')[file_header is not None and isinstance(file_header, str)]
            with open(filename, creation_mode, **kwargs) as f:
                if file_header is not None:
                    f.write(file_header)

        self.file_obj = open(filename, mode, **kwargs)

    def get_file_obj(self):
        return self.file_obj

    def __enter__(self):
        return self.get_file_obj()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_obj.close()


class TextFileEditor:
    def __init__(self, filename, file_header=None):
        self.original_filename = os.path.abspath(filename)
        self.backup_name = None
        if os.path.exists(self.original_filename):
            self.backup_name = os.path.join(
                common.get_temp_dir(),
                os.path.basename(filename) + '.bak'
            )
            os.rename(self.original_filename, self.backup_name)

        self.file_obj = open(self.original_filename, 'w')
        self.file_header = file_header
        self.canceled = False

    def read_contents(self):
        if self.backup_name is not None:
            with open(self.backup_name) as f:
                ret = f.read()
            return ret
        else:
            return self.file_header

    def write(self, contents):
        self.file_obj.write(contents)

    def close(self):
        self.file_obj.close()
        if self.backup_name is not None and os.path.exists(self.backup_name):
            os.remove(self.backup_name)

    def cancel(self):
        self.file_obj.close()
        os.remove(self.original_filename)
        if self.backup_name is not None and os.path.exists(self.backup_name):
            os.rename(self.backup_name, self.original_filename)
        self.canceled = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.canceled:
            if exc_type is None:
                self.close()
            else:
                self.cancel()

