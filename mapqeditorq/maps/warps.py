

from ..mqeq_logic.parsers import ParseableStructBase


class MapWarp(ParseableStructBase):
    FORMAT = (
        ('unk_0', 'u16'),
        ('unk_2', 'u16'),
        ('unk_4', 'u16'),
        ('unk_6', 'u16'),
        ('unk_8', 'u16'),
        ('unk_a', 'u8'),
        ('map_index', 'u8'),
        ('map_subindex', 'u8'),
        ('unk_d', 'u8'),
        ('unk_e', 'u8'),
        ('unk_f', 'u8'),
        ('unk_10', 'u16'),
        ('padding', 'u16')
    )

    def __init__(self):
        super().__init__()
        self.unk_0 = None
        self.unk_2 = None
        self.unk_4 = None
        self.unk_6 = None
        self.unk_8 = None
        self.unk_a = None
        self.map_index = None
        self.map_subindex = None
        self.unk_d = None
        self.unk_e = None
        self.unk_f = None
        self.unk_10 = None
        self.padding = None