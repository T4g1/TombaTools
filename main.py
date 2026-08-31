import sys
import asyncio
import logging
from PySide6 import QtWidgets
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QImage, QPixmap
from qasync import QEventLoop

from mainwindow_ui import Ui_MainWindow

from common import GuiLogger, logger
from connector.emulator import Emulator
from game.entity import Entity
from game.vram import Pixels
from worker import AbstractWorker
from worker.discover_entity import DiscoverEntityWorker
from worker.update_entity import UpdateEntity
from worker.vram_worker import VRAMWorker
from model.entity_table_model import EntityTableModel


class MainWindow(QtWidgets.QMainWindow):
    emulator: Emulator
    loop: asyncio.AbstractEventLoop

    discover_entity_worker: DiscoverEntityWorker
    vram_worker: VRAMWorker

    threadpool: QThreadPool
    workers: list[AbstractWorker]

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
        self.entity_model.signals.entity_updated.connect(self.on_entity_update)
        self.ui.entitiesTableView.setModel(self.entity_model)

        self.discover_entity_worker = DiscoverEntityWorker()
        self.discover_entity_worker.signals.entity_discovered.connect(
            self.on_entity_discovered
        )
        self.discover_entity_worker.setAutoDelete(False)

        self.vram_worker = VRAMWorker()
        self.vram_worker.signals.vram_loaded.connect(self.on_vram_loaded)

    def on_vram_loaded(self, pixels: Pixels):
        WIDTH = 1024

        raw_bytes = bytearray(
            value
            for pixel in pixels.data
            for value in (pixel.r, pixel.g, pixel.b, pixel.a)
        )

        bytes_per_line = WIDTH * 4
        image = QImage(
            raw_bytes,
            pixels.width,
            pixels.height,
            bytes_per_line,
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(image)
        self.ui.vram.setPixmap(pixmap)

    def on_action_connect(self):
        self.start_discover_entities()
        self.start_load_vram()

    def start_load_vram(self):
        if not self.vram_worker.is_working():
            self.entity_model.clear()

            self.threadpool.start(self.vram_worker)
        else:
            logger.info("Wait for the VRAM to be loaded fully first")

    def start_discover_entities(self):
        if not self.discover_entity_worker.is_working():
            self.entity_model.clear()

            self.threadpool.start(self.discover_entity_worker)
        else:
            logger.info("Wait for the entity discovery task to finish first")

    def closeEvent(self, event):
        self.on_action_quit()

    def on_action_quit(self):
        logger.info("Closing Tomba! tools gracefully...")

        for worker in self.workers:
            worker.kill()

        self.discover_entity_worker.kill()

        self.threadpool.waitForDone()
        instance = QtWidgets.QApplication.instance()
        if instance is not None:
            instance.quit()

    def on_entity_discovered(self, entity: Entity):
        logger.info(f"Found entity: {entity}")
        self.entity_model.addRow(entity)

    def on_entity_update(self, entity: Entity):
        worker = UpdateEntity(entity)
        self.threadpool.start(worker)
        self.workers.append(worker)


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(loop)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
