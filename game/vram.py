from dataclasses import dataclass

VRAM_HEIGHT = 512


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
