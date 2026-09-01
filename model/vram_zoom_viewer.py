from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QImage, QPixmap

from signals import VRAMHoverSignals
from game.vram import (
    VRAM_HEIGHT,
    BYTES_PER_LINE,
    COLOR_SIZE,
    get_clut_value,
    get_from_16bit_color,
    VRAMMode,
    Pixel,
)

from mainwindow_ui import Ui_MainWindow


class VRAMPixmapItem(QGraphicsPixmapItem):
    signals: VRAMHoverSignals

    def __init__(self, parent=None):
        super().__init__(parent)

        self.signals = VRAMHoverSignals()

        self.setAcceptHoverEvents(True)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverMoveEvent(event)

        self.signals.mouse_moved.emit(event.pos())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        super().mousePressEvent(event)

        if event.button() is Qt.MouseButton.RightButton:
            self.signals.mouse_click.emit(event.pos())


class VRAMZoomViewer(QGraphicsView):
    pixmap_item: VRAMPixmapItem
    mode: VRAMMode
    clut_address: int
    raw_data: bytearray

    ui: Ui_MainWindow

    def __init__(self, ui: Ui_MainWindow, parent=None):
        super().__init__(parent)

        self.mode = VRAMMode.DIRECT_COLOR
        self.clut_address = 0
        self.raw_data = bytearray()

        scene = QGraphicsScene(self)
        self.setScene(scene)

        self.pixmap_item = VRAMPixmapItem()
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

    def on_mouse_moved(self, position: QPointF):
        self.ui.statusbar.showMessage(f"X:{int(position.x())} Y:{int(position.y())}")

    def on_mouse_click(self, position: QPointF):
        if self.mode is VRAMMode.DIRECT_COLOR:
            self.ui.clut_x.setValue(int(position.x()) * 2)
            self.ui.clut_y.setValue(int(position.y()))
            self.update_clut()

    def on_clut_changed(self, _: int = 0):
        self.update_clut()

    def on_mode_changed(self, mode: int):
        self.mode = VRAMMode(mode)
        self.vram_refresh()

    def update_clut(self):
        x = self.ui.clut_x.value()
        y = self.ui.clut_y.value()

        self.clut_address = y * BYTES_PER_LINE + x
        self.vram_refresh()

    def vram_refresh(self):
        def add_pixel(pixels: bytearray, pixel: Pixel) -> bytearray:
            # TODO: Handle alpha channel
            pixel.a = 255
            pixels += pixel.r.to_bytes()
            pixels += pixel.g.to_bytes()
            pixels += pixel.b.to_bytes()
            pixels += pixel.a.to_bytes()
            return pixels

        bytes_per_pixel = 4

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
            width * bytes_per_pixel,
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(image)
        self.pixmap_item.setPixmap(pixmap)

    def on_vram_loaded(self, data: bytearray):
        self.raw_data = data
        self.vram_refresh()

    def wheelEvent(self, event):
        """Zooms into the image based on mouse wheel movement."""
        zoom_factor = 1.15

        if event.angleDelta().y() > 0:
            # Zoom In
            self.scale(zoom_factor, zoom_factor)
        elif event.angleDelta().y() < 0:
            # Zoom Out
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)

        event.accept()
