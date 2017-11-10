# -*- coding: utf-8 -*-

#                   (Signed?, Length)
DATA_TYPES = {'u8': (False, 1),
              's8': (True, 1),
              'u16': (False, 2),
              's16': (True, 2),
              'u32': (False, 4),
              's32': (True, 4)
              }


class StructureBase:
    """Example:
    FORMAT = (('value1', 'u8'),
            ('value2', 's16'),
            ...
            )"""
    FORMAT = None

    def load_from_bytes(self, data):
        i = 0
        for attribute, data_type in type(self).FORMAT:
            signed, data_size = DATA_TYPES[data_type]
            setattr(self, attribute, int.from_bytes(data[i:i + data_size], 'little', signed=signed))
            i += data_size
        # print(self)

    def to_bytes(self):
        data = b''
        for attribute, data_type in type(self).FORMAT:
            signed, data_size = DATA_TYPES[data_type]
            data += getattr(self, attribute).to_bytes(data_size, 'little', signed=signed)
        return data

    @classmethod
    def size(cls):
        ret = 0
        for attribute, data_type in cls.FORMAT:
            ret += DATA_TYPES[data_type][1]
        return ret

    def __repr__(self):
        ret = type(self).__name__ + ' {'
        for attribute, data_type in type(self).FORMAT:
            ret += ' {0} {1}: {2},'.format(data_type, attribute, hex(getattr(self, attribute)))
        return ret + '}'
