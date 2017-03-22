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

    def to_bytes(self):
        data = b''
        for attribute, data_type in type(self).FORMAT:
            signed, data_size = DATA_TYPES[data_type]
            data += getattr(self, attribute).to_bytes(data_size, 'little', signed=signed)
        return data

