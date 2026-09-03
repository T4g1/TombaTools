from bitutils import TypeSize, read_int


class Frame:
    SIZE = 16

    def __init__(self, raw: bytearray, vram_page_offset: int):
        self.raw = raw.copy()

        self.top_left_x = raw[0x00]
        self.top_left_y = raw[0x01]
        self.clut = read_int(raw, 0x02, TypeSize.HALF_WORD, byteorder="little") * 32
        self.top_right_x = raw[0x04]
        self.top_right_y = raw[0x05]
        self.vram_page = (
            read_int(raw, 0x06, TypeSize.HALF_WORD, byteorder="little")
            + vram_page_offset
        )
        self.bottom_left_x = raw[0x08]
        self.bottom_left_y = raw[0x09]
        self.width = raw[0x0A]
        self.height = raw[0x0B]
        self.bottom_right_x = raw[0x0C]
        self.bottom_right_y = raw[0x0D]
        self.offset_x = int.from_bytes(raw[0x0E:0x0F], signed=True)
        self.offset_y = int.from_bytes(raw[0x0F:0x10], signed=True)

    def __str__(self):
        return (
            f"TL: x:{self.top_left_x} y:{self.top_left_y} - "
            f"TR: x:{self.top_right_x} y:{self.top_right_y} - "
            f"BL: x:{self.bottom_left_x} y:{self.bottom_left_y} - "
            f"BR: x:{self.bottom_right_x} y:{self.bottom_right_y} - "
            f"size: x:{self.width} y:{self.height} - "
            f"off: x:{self.offset_x} y:{self.offset_y} - "
            f"VRAM page: {self.vram_page} CLUT: 0x{self.clut:04X}"
        )
