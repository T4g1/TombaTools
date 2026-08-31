import sys
import asyncio
import logging
from PySide6 import QtWidgets
from PySide6.QtCore import QThreadPool
from qasync import QEventLoop

from mainwindow_ui import Ui_MainWindow

from common import GuiLogger, logger
from connector.emulator import Emulator
from game.entity import Entity
from worker.discover_entity import DiscoverEntityWorker
from worker.update_entity import UpdateEntity
from model.entity_table_model import EntityTableModel


class MainWindow(QtWidgets.QMainWindow):
    emulator: Emulator
    loop: asyncio.AbstractEventLoop

    discover_entity_worker: DiscoverEntityWorker

    def __init__(self, loop):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        log_handler = GuiLogger(self.ui.logTextBox)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

        self.ui.actionConnect.triggered.connect(self.on_action_connect)

        self.loop = loop

        self.entity_model = EntityTableModel()
        self.entity_model.signals.entity_updated.connect(self.on_entity_update)
        self.ui.entitiesTableView.setModel(self.entity_model)

        self.discover_entity_worker = DiscoverEntityWorker()
        self.discover_entity_worker.signals.entity_discovered.connect(
            self.on_entity_discovered
        )
        self.discover_entity_worker.setAutoDelete(False)

    def on_action_connect(self):
        if not self.discover_entity_worker.is_working():
            self.entity_model.clear()

            QThreadPool.globalInstance().start(self.discover_entity_worker)
        else:
            logger.info("Wait for the entity discovery task to finish first")

    def on_entity_discovered(self, entity: Entity):
        logger.info(f"Found entity: {entity}")
        self.entity_model.addRow(entity)

    def on_entity_update(self, entity: Entity):
        worker = UpdateEntity(entity)
        QThreadPool.globalInstance().start(worker)


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(loop)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
