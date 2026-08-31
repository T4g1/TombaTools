from PySide6.QtCore import QRunnable

from connector.emulator import Emulator
from signals import EntitySignals


class EntityWorker(QRunnable):
    psx: Emulator
    signals: EntitySignals

    working: bool

    def __init__(self):
        super().__init__()
        self.signals = EntitySignals()

        self.working = False

    def is_working(self) -> bool:
        return self.working

    def run(self):
        pass
