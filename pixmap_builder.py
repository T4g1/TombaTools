from typing import cast

from PySide6.QtGui import QPainter, QPaintDevice
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

from game.entity import Entity
from game.frame import Frame
from game.vram import (
    BYTES_PER_LINE,
    Pixel,
    get_clut_value,
    PAGES_PER_LINE,
    PAGE_HEIGHT,
    PAGE_WIDTH,
)

BYTES_PER_PIXEL = 4


def add_pixel(pixels: bytearray, pixel: Pixel) -> bytearray:
    pixels += pixel.r.to_bytes()
    pixels += pixel.g.to_bytes()
    pixels += pixel.b.to_bytes()
    pixels += pixel.a.to_bytes()
    return pixels


def build_preview(
    frames: list[Frame], vram_data: bytearray, entity: Entity | None = None
):
    """Build a preview from given frames"""
    # Compute image size
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    for frame in frames:
        min_x = min(min_x, frame.offset_x)
        min_y = min(min_y, frame.offset_y)

        max_x = max(max_x, frame.offset_x + frame.width)
        max_y = max(max_y, frame.offset_y + frame.height)

    total_width = max_x - min_x
    total_height = max_y - min_y

    extended_pixmap = QPixmap(total_width, total_height)
    extended_pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter()
    painter.begin(cast(QPaintDevice, extended_pixmap))

    bytes_per_pixel = 4

    for frame in reversed(frames):
        page_x = frame.vram_page % PAGES_PER_LINE
        page_y = (frame.vram_page // PAGES_PER_LINE) % 2

        start_x = page_x * PAGE_WIDTH
        start_y = page_y * PAGE_HEIGHT

        width = frame.bottom_right_x - frame.top_left_x
        height = frame.bottom_right_y - frame.top_left_y

        clut = frame.clut
        if entity is not None and entity.clut != 0x00:
            clut = entity.clut

        pixels: bytearray = bytearray()
        for y in range(start_y + frame.top_left_y, start_y + frame.bottom_right_y):
            for x in range(start_x + frame.top_left_x, start_x + frame.bottom_right_x):
                # Mode: 4bit per pixel
                index = (y * BYTES_PER_LINE) + x // 2
                shift = 4 * (x % 2)
                clut_index = vram_data[index] >> shift & 0x0F
                pixel = get_clut_value(vram_data, clut, clut_index)
                pixels = add_pixel(pixels, pixel)

        image = QImage(
            pixels,
            width,
            height,
            width * bytes_per_pixel,
            QImage.Format.Format_RGBA8888,
        )
        pixmap = QPixmap.fromImage(image)
        painter.drawPixmap(
            abs(min_x) + frame.offset_x, abs(min_y) + frame.offset_y, pixmap
        )

    painter.end()

    return extended_pixmap
