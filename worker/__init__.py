from PySide6.QtCore import QRunnable

from connector.emulator import Emulator


class AbstractWorker(QRunnable):
    psx: Emulator

    working: bool

    def __init__(self, psx: Emulator):
        super().__init__()
        self.psx = psx
        self.working = False

    def is_working(self) -> bool:
        return self.working

    def run(self):
        pass

    def kill(self):
        self.working = False
