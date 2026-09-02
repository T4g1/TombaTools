import sys
import asyncio
import logging
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QGraphicsScene,
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QThreadPool, QThread, Signal, QItemSelection
from qasync import QEventLoop

from mainwindow_ui import Ui_MainWindow

from common import GuiLogger, logger
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
from worker import AbstractWorker
from worker.emulator_worker import EmulatorWorker
from model.entity_table_model import EntityTableModel, EntityColumns
from model.vram_zoom_viewer import VRAMZoomViewer
from model.pixmap_item import PixmapItem


class MainWindow(QtWidgets.QMainWindow):
    psx: EmulatorWorker
    loop: asyncio.AbstractEventLoop

    vram_zoom_viewer: VRAMZoomViewer
    entity_preview: PixmapItem

    threadpool: QThreadPool
    workers: list[AbstractWorker]

    load_vram = Signal()
    load_entities = Signal()
    load_preview = Signal(Entity)
    update_entity = Signal(Entity)

    def __init__(self, loop):
        super().__init__()

        self.workers = []
        self.threadpool = QThreadPool()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        log_handler = GuiLogger(self.ui.logTextBox)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

        self.ui.actionConnect.triggered.connect(self.on_action_connect)
        self.ui.actionQuit.triggered.connect(self.on_action_quit)

        self.loop = loop

        self.entity_model = EntityTableModel()
        self.entity_model.entity_updated.connect(self.on_entity_update)
        self.ui.entitiesTableView.setModel(self.entity_model)
        self.ui.entitiesTableView.selectionModel().selectionChanged.connect(
            self.on_entity_cell_selected
        )

        scene = QGraphicsScene(self)
        self.entity_preview = PixmapItem()
        scene.addItem(self.entity_preview)
        self.ui.entity_preview.setScene(scene)

        self.vram_zoom_viewer = VRAMZoomViewer(self.ui)
        vram_layout = self.ui.tab_vram.layout()
        assert vram_layout is not None
        vram_layout.addWidget(self.vram_zoom_viewer)

        self.emulator_worker = EmulatorWorker()

        self.psx_thread = QThread()
        self.psx = EmulatorWorker()
        self.psx_thread.started.connect(self.psx.connect)
        self.psx.connected.connect(self.on_psx_connected)
        self.psx.vram_loaded.connect(self.vram_zoom_viewer.on_vram_loaded)
        self.psx.entity_loaded.connect(self.on_entity_loaded)
        self.psx.preview_loaded.connect(self.on_preview_loaded)
        self.psx.moveToThread(self.psx_thread)

        self.load_vram.connect(self.psx.load_vram)
        self.load_entities.connect(self.psx.load_entities)
        self.load_preview.connect(self.psx.load_preview)
        self.update_entity.connect(self.psx.update_entity)

    def on_action_connect(self):
        if not self.psx_thread.isRunning():
            self.psx_thread.start()

    def on_psx_connected(self):
        self.start_load_entities()
        self.start_load_vram()

    def closeEvent(self, event):
        self.on_action_quit()

    def on_action_quit(self):
        logger.info("Closing Tomba! tools gracefully...")

        if hasattr(self, "psx_thread") and self.psx_thread.isRunning():
            self.psx_thread.quit()
            self.psx_thread.wait()

        for worker in self.workers:
            worker.kill()

        self.threadpool.waitForDone()
        instance = QtWidgets.QApplication.instance()
        if instance is not None:
            instance.quit()

    def on_entity_loaded(self, entity: Entity):
        logger.info(f"Found entity: {entity}")
        self.entity_model.addRow(entity)

    def start_load_vram(self):
        self.load_vram.emit()

    def start_load_entities(self):
        self.load_entities.emit()

    def on_entity_update(self, entity: Entity):
        self.update_entity.emit(entity)

    def on_entity_cell_selected(self, selected: QItemSelection, _: QItemSelection):
        new_indexes = selected.indexes()

        if len(new_indexes) != 1:
            return

        index = new_indexes[0]

        entity = self.entity_model.entities[index.row()]
        self.load_preview.emit(entity)

        if index.column() != EntityColumns.CLUT:
            return

        self.vram_zoom_viewer.set_clut_by_value(entity.clut)

    def on_preview_loaded(self, frame: Frame):
        def add_pixel(pixels: bytearray, pixel: Pixel) -> bytearray:
            # TODO: Handle alpha channel
            pixel.a = 255
            pixels += pixel.r.to_bytes()
            pixels += pixel.g.to_bytes()
            pixels += pixel.b.to_bytes()
            pixels += pixel.a.to_bytes()
            return pixels

        bytes_per_pixel = 4

        page_x = frame.vram_page % PAGES_PER_LINE
        page_y = (frame.vram_page // PAGES_PER_LINE) % 2

        start_x = page_x * PAGE_WIDTH
        start_y = page_y * PAGE_HEIGHT

        raw_data = self.vram_zoom_viewer.raw_data

        width = frame.bottom_right_x - frame.top_left_x
        height = frame.bottom_right_y - frame.top_left_y

        pixels: bytearray = bytearray()
        for y in range(start_y + frame.top_left_y, start_y + frame.bottom_right_y):
            for x in range(start_x + frame.top_left_x, start_x + frame.bottom_right_x):
                # Mode: 4bit per pixel
                index = (y * BYTES_PER_LINE) + x // 2
                shift = 4 * (x % 2)
                clut_index = raw_data[index] >> shift & 0x0F
                pixel = get_clut_value(raw_data, frame.clut, clut_index)
                pixels = add_pixel(pixels, pixel)

        image = QImage(
            pixels,
            width,
            height,
            width * bytes_per_pixel,
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(image)
        self.entity_preview.setPixmap(pixmap)
        self.entity_preview.setScale(2.0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(loop)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
