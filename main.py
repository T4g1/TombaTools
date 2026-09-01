import sys
import asyncio
import logging
from PySide6 import QtWidgets
from PySide6.QtCore import QThreadPool, QThread, Signal
from qasync import QEventLoop

from mainwindow_ui import Ui_MainWindow

from common import GuiLogger, logger
from game.entity import Entity
from worker import AbstractWorker
from worker.emulator_worker import EmulatorWorker
from model.entity_table_model import EntityTableModel
from model.vram_zoom_viewer import VRAMZoomViewer


class MainWindow(QtWidgets.QMainWindow):
    psx: EmulatorWorker
    loop: asyncio.AbstractEventLoop

    vram_zoom_viewer: VRAMZoomViewer

    threadpool: QThreadPool
    workers: list[AbstractWorker]

    load_vram = Signal()
    load_entities = Signal()
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
        self.entity_model.signals.entity_updated.connect(self.on_entity_update)
        self.ui.entitiesTableView.setModel(self.entity_model)

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
        self.psx.moveToThread(self.psx_thread)

        self.load_vram.connect(self.psx.load_vram)
        self.load_entities.connect(self.psx.load_entities)
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(loop)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
