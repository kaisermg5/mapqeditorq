
import abc
import os

from . import common
from . import file_utils
from .parsers import CParser, DefinitionNotFoundError, CDefinition


class BaseTable(abc.ABC):
    def __init__(self, filename, definition):
        self.filename = filename
        self.definition = definition
        self.table = None

        self.modified = False

        self.extern_entries = []

    @abc.abstractmethod
    def extract_array(self, game):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def parse_array(self, txt):
        raise NotImplementedError('You must override this')

    def load(self, game):
        with file_utils.EasyOpen(self.filename, file_header=common.MAP_FILES_INCLUDES) as f:
            contents = f.read()
            try:
                self.table = self.parse_array(contents)
            except DefinitionNotFoundError:
                self.table = self.extract_array(game)
                self.save()

    def add_dependencies_prototypes(self, original_txt, new_txt):
        for extern in self.extern_entries:
            if not CParser.is_prototype_declared(extern, original_txt):
                new_txt = '{0}\n\n{1}'.format(extern.as_prototype(), new_txt)
        return new_txt

    def save(self):
        with file_utils.TextFileEditor(self.filename, file_header=common.MAP_FILES_INCLUDES) as f:
            txt = f.read_contents()
            new_txt = self.get_initialization_text()
            new_txt = self.add_dependencies_prototypes(txt, new_txt)
            txt = CParser.change_initialization(
                txt, self.definition, new_txt
            )
            f.write(txt)
        self.modified = False

    def loaded(self):
        return self.table is not None

    def __getitem__(self, item):
        return self.table[item]

    def __setitem__(self, key, value):
        if isinstance(value, CDefinition):
            self.extern_entries.append(value)
            self.table[key] = '&' + value.get_label()
        else:
            self.table[key] = value
        if not self.was_modified():
            self.modified = True

    def __len__(self):
        return len(self.table)

    def was_modified(self):
        return self.modified

    def discard_changes(self):
        if self.was_modified():
            self.table = None
            self.modified = False

    def get_label(self):
        return self.definition.get_label()

    def get_initialization_text(self):
        ret = CParser.format_initialization(
            self.definition,
            CParser.format_array_contents(self.table)
        )
        return ret

    def get_array(self):
        return self.table


class StructTableBase(BaseTable):
    StructClass = None

    def parse_array(self, txt):
        struct_strings = CParser.parse_struct_array(txt, self.definition)
        struct_count = len(struct_strings)
        array = [None] * struct_count
        for i in range(struct_count):
            header = self.StructClass()
            header.load_from_c_format(struct_strings[i])
            array[i] = header
        return array

    def add_dependencies_prototypes(self, original_txt, new_txt):
        new_txt = super().add_dependencies_prototypes(original_txt, new_txt)
        for s in self.table:
            for dependency in s.dependencies:
                if not CParser.is_prototype_declared(dependency, original_txt):
                    new_txt = '{0}\n\n{1}'.format(dependency.as_prototype(), new_txt)
        return new_txt

    def was_modified(self):
        if super().was_modified():
            return True
        if self.table is not None:
            for s in self.table:
                if s.was_modified():
                    return True
        return False


class NumberTableBase(BaseTable):
    def parse_array(self, txt):
        return CParser.parse_number_array(txt, self.definition)


class IncludedBinaryFileBase(abc.ABC):
    def __init__(self, data_filename, definition_filename, definition, assigned_object, compressed=True):
        self.data_filename = data_filename
        self.definition_filename = definition_filename
        self.definition = definition
        self.assignd_object = assigned_object
        self.compressed = compressed

    @abc.abstractmethod
    def extract_data(self, game):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def set_data_to_object(self, data):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def was_modified(self):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def after_saving_object_update(self):
        raise NotImplementedError('You must override this')

    @abc.abstractmethod
    def get_data_from_object(self):
        raise NotImplementedError('You must override this')

    def load_data(self, game):
        if not os.path.exists(self.data_filename):
            data = self.extract_data(game)
        else:
            with open(self.data_filename, 'rb') as f:
                data = f.read()
        self.set_data_to_object(data)

    def save(self):
        data = self.get_data_from_object()
        with file_utils.EasyOpen(self.data_filename, 'wb') as f:
            f.write(data)

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

        self.after_saving_object_update()

    def get_initialization_text(self):
        if self.compressed:
            filename = common.resource_path_join('build', self.data_filename + '.lz')
        else:
            filename = self.data_filename
        return CParser.format_incbin(self.definition, filename)


