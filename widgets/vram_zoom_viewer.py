from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QImage, QPixmap, QBrush, QColor

from common import wheel_zoom
from game.vram import (
    VRAM_HEIGHT,
    BYTES_PER_LINE,
    COLOR_SIZE,
    get_clut_value,
    get_from_16bit_color,
    VRAMMode,
)
from pixmap_builder import add_pixel, BYTES_PER_PIXEL
from widgets.pixmap_item import PixmapItem
from mainwindow_ui import Ui_MainWindow


class VRAMZoomViewer(QGraphicsView):
    pixmap_item: PixmapItem
    mode: VRAMMode
    clut_address: int
    raw_data: bytearray

    ui: Ui_MainWindow

    def __init__(self, ui: Ui_MainWindow, parent=None):
        super().__init__(parent)

        self.mode = VRAMMode.DIRECT_COLOR
        self.clut_address = 0
        self.raw_data = bytearray()

        self.setAutoFillBackground(True)
        brush = QBrush(QColor(125, 125, 125, 255))
        brush.setStyle(Qt.BrushStyle.Dense2Pattern)
        self.setBackgroundBrush(brush)

        scene = QGraphicsScene(self)
        self.setScene(scene)

        self.pixmap_item = PixmapItem()
        self.pixmap_item.signals.mouse_click.connect(self.on_mouse_click)
        self.pixmap_item.signals.mouse_moved.connect(self.on_mouse_moved)
        scene.addItem(self.pixmap_item)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMouseTracking(True)

        self.setRenderHint(self.renderHints().SmoothPixmapTransform)

        self.ui = ui
        self.ui.mode.currentIndexChanged.connect(self.on_mode_changed)
        self.ui.clut_x.valueChanged.connect(self.on_clut_changed)
        self.ui.clut_y.valueChanged.connect(self.on_clut_changed)

        self.wheelEvent = lambda event: wheel_zoom(self, event)

    def get_x_from_mode(self, x: int) -> int:
        if self.mode is VRAMMode.DIRECT_COLOR:
            return x * COLOR_SIZE
        elif self.mode is VRAMMode.CLUT_256:
            return x
        elif self.mode is VRAMMode.CLUT_16:
            return x // 2

        return x

    def set_clut_by_value(self, value: int):
        clut_value = value * 32

        x = clut_value % BYTES_PER_LINE
        y = clut_value // BYTES_PER_LINE

        self.set_clut(x, y)

    def set_clut(self, x: int, y: int):
        self.ui.clut_y.setValue(y)
        self.ui.clut_x.setValue(x)
        self.update_clut()

    def on_mouse_moved(self, position: QPointF):
        x = self.get_x_from_mode(int(position.x()))
        y = int(position.y())
        self.ui.statusbar.showMessage(f"X:{x} Y:{y}")

    def on_mouse_click(self, position: QPointF):
        self.set_clut(self.get_x_from_mode(int(position.x())), int(position.y()))

    def on_clut_changed(self, _: int = 0):
        self.update_clut()

    def on_mode_changed(self, mode: int):
        self.mode = VRAMMode(mode)
        self.vram_refresh()

        self.resetTransform()
        self.centerOn(0, 0)

    def update_clut(self):
        x = self.ui.clut_x.value()
        y = self.ui.clut_y.value()

        self.clut_address = y * BYTES_PER_LINE + x
        self.vram_refresh()

    def vram_refresh(self):
        width = 1024
        if self.mode is VRAMMode.CLUT_256:
            width = 2048
        elif self.mode is VRAMMode.CLUT_16:
            width = 4096

        pixels: bytearray = bytearray()
        for y in range(VRAM_HEIGHT):
            for x in range(width):
                index = (y * BYTES_PER_LINE) + x
                if self.mode is VRAMMode.DIRECT_COLOR:
                    index = (y * BYTES_PER_LINE) + x * COLOR_SIZE
                    raw_value = self.raw_data[index : index + COLOR_SIZE]
                    pixel = get_from_16bit_color(
                        int.from_bytes(raw_value, byteorder="little")
                    )
                    pixels = add_pixel(pixels, pixel)

                elif self.mode is VRAMMode.CLUT_256:
                    index = (y * BYTES_PER_LINE) + x
                    clut_index = self.raw_data[index]
                    pixel = get_clut_value(self.raw_data, self.clut_address, clut_index)
                    pixels = add_pixel(pixels, pixel)

                elif self.mode is VRAMMode.CLUT_16:
                    index = (y * BYTES_PER_LINE) + x // 2
                    shift = 4 * (x % 2)
                    clut_index = self.raw_data[index] >> shift & 0x0F
                    pixel = get_clut_value(self.raw_data, self.clut_address, clut_index)
                    pixels = add_pixel(pixels, pixel)

        image = QImage(
            pixels,
            width,
            VRAM_HEIGHT,
            width * BYTES_PER_PIXEL,
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(image)
        self.pixmap_item.setPixmap(pixmap)

    def on_vram_loaded(self, data: bytearray):
        self.raw_data = data
        self.vram_refresh()
