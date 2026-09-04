import sys
import asyncio
import logging
from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QThreadPool, QThread, Signal, QItemSelection
from qasync import QEventLoop

from mainwindow_ui import Ui_MainWindow

from common import GuiLogger, logger
from game.entity import Entity
from worker import AbstractWorker
from worker.emulator_worker import EmulatorWorker
from widgets.entity_table_model import EntityTableModel
from widgets.vram_zoom_viewer import VRAMZoomViewer
from widgets.entity_widget import EntityWidget


class MainWindow(QtWidgets.QMainWindow):
    psx: EmulatorWorker
    loop: asyncio.AbstractEventLoop

    vram_zoom_viewer: VRAMZoomViewer
    pixmap_preview: QPixmap | None = None

    threadpool: QThreadPool
    workers: list[AbstractWorker]

    load_vram = Signal()
    load_entities = Signal()
    preview_entity = Signal(Entity)

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

        self.vram_zoom_viewer = VRAMZoomViewer(self.ui)
        vram_layout = self.ui.tab_vram.layout()
        assert vram_layout is not None
        vram_layout.addWidget(self.vram_zoom_viewer)

        self.emulator_worker = EmulatorWorker()

        self.entity_widget = EntityWidget(self.vram_zoom_viewer)
        self.ui.entity_viewer_layout.addWidget(self.entity_widget)

        self.psx_thread = QThread()
        self.psx = EmulatorWorker()
        self.psx_thread.started.connect(self.psx.connect)
        self.psx.connected.connect(self.on_psx_connected)
        self.psx.vram_loaded.connect(self.vram_zoom_viewer.on_vram_loaded)
        self.psx.entity_loaded.connect(self.on_entity_loaded)
        self.psx.moveToThread(self.psx_thread)

        self.entity_model = EntityTableModel()
        self.entity_model.entity_updated.connect(self.psx.update_entity)
        self.ui.entitiesTableView.setModel(self.entity_model)
        self.ui.entitiesTableView.selectionModel().selectionChanged.connect(
            self.on_entity_cell_selected
        )

        self.entity_widget.update_entity.connect(self.psx.update_entity)
        self.entity_widget.load_preview.connect(self.psx.load_preview)
        self.entity_widget.refresh_entity.connect(self.psx.refresh_entity)
        self.psx.preview_frames.connect(self.entity_widget.on_preview_frames)
        self.psx.entity_refreshed.connect(self.entity_widget.on_refresh)
        self.psx.entity_refreshed.connect(self.entity_model.on_entity_updated)

        self.load_vram.connect(self.psx.load_vram)
        self.load_entities.connect(self.psx.load_entities)
        self.preview_entity.connect(self.entity_widget.on_preview_entity)

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

    def on_entity_cell_selected(self, selected: QItemSelection, _: QItemSelection):
        new_indexes = selected.indexes()

        if len(new_indexes) != 1:
            return

        index = new_indexes[0]

        entity = self.entity_model.entities[index.row()]
        self.preview_entity.emit(entity)


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(loop)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
