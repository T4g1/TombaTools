import enum

from dataclasses import dataclass

VRAM_HEIGHT = 512
BYTES_PER_LINE = 2048
PAGE_WIDTH = 256
PAGE_HEIGHT = 256
PAGES_PER_LINE = 16

COLOR_SIZE = 2


class VRAMMode(enum.IntEnum):
    DIRECT_COLOR = 0
    CLUT_256 = 1
    CLUT_16 = 2


@dataclass
class Pixel:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass
class Pixels:
    data: list[Pixel]
    width: int
    height: int = VRAM_HEIGHT


def get_from_16bit_color(value: int, inverted: bool = False) -> Pixel:
    """Two bytes of data"""
    red = (value >> 0) & 0x1F
    green = (value >> 5) & 0x1F
    blue = (value >> 10) & 0x1F
    alpha = (value >> 15) & 0x01

    red = (red * 255) // 31
    green = (green * 255) // 31
    blue = (blue * 255) // 31
    alpha = (1 - alpha) * 255

    if inverted:
        red = 255 - red
        green = 255 - green
        blue = 255 - blue

    return Pixel(red, green, blue, alpha)


def get_clut_value(data: bytearray, clut_address: int, color_index: int) -> Pixel:
    clut_value_index = clut_address + color_index * COLOR_SIZE
    value = int.from_bytes(
        data[clut_value_index : clut_value_index + COLOR_SIZE], byteorder="little"
    )
    return get_from_16bit_color(value)
