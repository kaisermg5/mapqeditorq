
import re

from ..game.structure_utils import StructureBase


class ParsignError(Exception):
    pass


class DefinitionNotFoundError(ParsignError):
    pass


def hex_format(num, digits=2):
    return ('{0:0>' + str(digits) + '}').format(hex(num)[2::])


class CParser:
    @staticmethod
    def get_custom_initialization_pattern(definition, start_pattern, end_pattern, unlimited=True):
        pattern = ('', r'.*')[unlimited] + definition.to_regex() \
                  + r'\s*=\s*' + start_pattern + r'(.*?)' + end_pattern \
                  + r'\s*;' + ('', r'.*')[unlimited]
        return pattern

    @classmethod
    def get_initialization_pattern(cls, definition, group_curly_brackets=True, unlimited=True):
        pattern = cls.get_custom_initialization_pattern(
            definition,
            (r'\{\s*', '')[group_curly_brackets],
            (r'\s*\}', '')[group_curly_brackets],
            unlimited
        )
        return pattern

    @staticmethod
    def remove_comments(txt):
        no_block_comments = re.sub(r'/\*.*?\*/', r'', txt, flags=re.DOTALL)
        no_line_comments = re.sub(r'//.*', r'', no_block_comments, flags=re.DOTALL)
        return no_line_comments

    @classmethod
    def get_array_contents_text(cls, txt, definition):
        txt = cls.remove_comments(txt)
        pattern = cls.get_initialization_pattern(definition, group_curly_brackets=False)
        m = re.match(pattern, txt, re.DOTALL)
        if m is None:
            raise DefinitionNotFoundError('Array definition specified not found.')

        array_contents_txt = m.group(1)
        if array_contents_txt and array_contents_txt[-1] != ',':
            array_contents_txt += ','
        return array_contents_txt

    @classmethod
    def parse_struct_array(cls, txt, definition):
        array_contents_txt = cls.get_array_contents_text(txt, definition)

        array_contents = []
        it = re.finditer(r'\s*(\{.*?\})\s*,', array_contents_txt, flags=re.DOTALL)
        for matcher in it:
            array_contents.append(matcher.group(1))

        return array_contents

    @staticmethod
    def parse_comma_separated_num(txt):
        ret = []
        it = re.finditer(r'\s*(.+?)\s*,', txt, re.DOTALL)
        for matcher in it:
            value = matcher.group(1)
            try:
                value = int(value, base=0)
            except ValueError:
                if not value:
                    value = 0
            ret.append(value)
        return ret

    @classmethod
    def parse_number_array(cls, txt, definition):
        array_contents_txt = cls.get_array_contents_text(txt, definition)
        return cls.parse_comma_separated_num(array_contents_txt)

    @classmethod
    def change_initialization(cls, old_txt, definition, new_initialization):
        pattern = cls.get_initialization_pattern(definition, unlimited=False)
        if cls.is_definition_in_text(definition, old_txt):
            new_txt = re.sub(pattern, new_initialization, old_txt, flags=re.DOTALL)
        else:
            new_txt = old_txt + '\n\n' + new_initialization

        return new_txt

    @staticmethod
    def is_definition_in_text(definition, text):
        pattern = r'.*' + definition.to_regex() + r'.*'
        m = re.match(pattern, text, re.DOTALL)
        return m is not None

    @staticmethod
    def is_prototype_declared(definition, text):
        pattern = r'.*' + definition.to_regex() + r'\s*;.*'
        m = re.match(pattern, text, re.DOTALL)
        return m is not None

    @staticmethod
    def format_initialization(definition, contents):
        return definition.to_c_format() + ' = {\n' + contents + '};\n\n'

    @staticmethod
    def format_array_contents(array):
        contents = ''
        for entry in array:
            if isinstance(entry, int):
                entry = hex(entry)
            contents += '\t{0},\n'.format(entry)
        return contents

    @staticmethod
    def format_incbin(definition, filename):
        return '{0} = INCBIN_U8("{1}");'.format(definition, filename)

    @staticmethod
    def format_incbin_array(definition, filenames):
        ret = definition.to_c_format() + ' = {\n'
        for filename in filenames:
            ret += '\tINCBIN_U8("{0}"),\n'.format(filename)
        return ret + '};'

    @classmethod
    def get_filename_from_incbin(cls, txt, definition):
        pattern = cls.get_custom_initialization_pattern(
            definition,
            r'INCBIN_U8\(\s*\"',
            r'\"\)\s*'
        )
        m = re.match(pattern, txt, re.DOTALL)
        if m is None:
            raise DefinitionNotFoundError('Binary inclusion not found.')
        return m.group(1)


class CDefinition:
    STATIC = 1
    EXTERN = 2

    def __init__(self, type, label, base_format='{0}', visibility=None):
        self.type = type
        self.label = label
        self.base_format = base_format
        self.visibility = visibility

    def copy(self):
        c = CDefinition(self.type, self.label, self.base_format, self.visibility)
        return c

    def as_extern(self):
        c = self.copy()
        c.visibility = self.EXTERN
        return c

    def as_prototype(self):
        return self.to_c_format() + ';'

    def get_label(self):
        return self.label

    def to_c_format(self):
        if self.visibility == self.STATIC:
            ret = 'static '
        elif self.visibility == self.EXTERN:
            ret = 'extern '
        else:
            ret = ''
        ret += self.type + ' '
        ret += ''.join(self.base_format.format(self.label).split())
        return ret

    def to_regex(self):
        if self.visibility == self.STATIC:
            ret = r'static\s+'
        elif self.visibility == self.EXTERN:
            ret = r'extern\s+'
        else:
            ret = ''
        ret += r'\s+'.join(self.type.strip().split()) + r'\s+'
        ret += r'\s*'.join(
            re.escape(part) for part in self.base_format.format(self.label).split()
        )
        return ret

    def __repr__(self):
        return self.to_c_format()

    def format_label(self, *args):
        self.label = self.label.format(*args)


class AsmParser:
    @staticmethod
    def format_repoints(label, addresses):
        ret = ''
        for address in addresses:
            ret += '\n.org {0}\n\t.word {1}\n'.format(hex(address), label)
        return ret



class ParseableStructBase(StructureBase):
    ATTR_STR_MASK = {}

    def __init__(self):
        self.modified = False
        self.dependencies = []

    def to_c_format(self):
        data = '{ '
        for attr, attr_size in self.FORMAT:
            if data != '{ ':
                data += ', '
            value = getattr(self, attr)
            if isinstance(value, int):
                value = hex(value)
                if attr in self.ATTR_STR_MASK:
                    value = self.ATTR_STR_MASK[attr].format(value)
            data += value
        return data + ' }'

    def load_from_c_format(self, txt):
        m = re.match(r'\s*\{\s*(.*?)\s*\}\s*', txt, re.DOTALL)
        if m is None:
            raise ParsignError('Could not parse "{}" into a structure.'.format(txt))
        no_brackets_txt = m.group(1)
        if no_brackets_txt and no_brackets_txt[-1] != ',':
            no_brackets_txt += ','

        values = CParser.parse_comma_separated_num(no_brackets_txt)
        for i in range(len(self.FORMAT)):
            if i < len(values):
                setattr(self, self.FORMAT[i][0], values[i])
            else:
                setattr(self, self.FORMAT[i][0], 0)

    def __repr__(self):
        return self.to_c_format()

    def was_modified(self):
        return self.modified

    def add_dependency(self, definition):
        self.dependencies.append(definition)


def get_16_color_palette_from_pal_file_format(file_contents):
    pattern = r'JASC-PAL\r\n0100\r\n16\r\n(\d{1,3} \d{1,3} \d{1,3}\r\n){16}'
    m = re.match(pattern, file_contents)
    if m is None:
        raise ParsignError('Not a valid pal file')
    lines = file_contents.split('\n')
    palette = []
    for i in range(3, 19):
        for value in lines[i].split():
            value = int(value)
            if value > 255:
                raise ParsignError('Not a valid pal file')
            palette.append(value)
    return palette


def convert_16_color_palette_to_pal_file_format(palette):
    ret = 'JASC-PAL\n0100\n16\n'
    for i in range(16):
        ret += '{0} {1} {2}\n'.format(*(palette[i * 3:i * 3 + 3]))
    return ret




