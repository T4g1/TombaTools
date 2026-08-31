from PySide6.QtNetwork import QUdpSocket

from worker import AbstractWorker
from signals import VRAMSignals
from connector.retroarch import RetroArch
from common import logger
from game.vram import Pixel, Pixels, VRAM_HEIGHT


class VRAMWorker(AbstractWorker):
    signals: VRAMSignals

    def __init__(self):
        super().__init__()
        self.signals = VRAMSignals()

    def run(self):
        self.working = True

        try:
            socket = QUdpSocket()
            self.psx = RetroArch(address="127.0.0.1", port=55355, socket=socket)
            self.psx.connect()

            logger.info("Loading VRAM...")
            self.load_vram()
        except Exception as exception:
            logger.error(exception)
        finally:
            self.psx.disconnect()

        if not self.working:
            return

        logger.info("Finished loading VRAM")
        self.working = False

    def load_vram(self):
        pixels: list[Pixel] = []

        WIDTH = 2048
        for x in range(WIDTH):
            for y in range(VRAM_HEIGHT):
                pixels.append(Pixel(x % 255, y % 255, 0))

        self.signals.vram_loaded.emit(Pixels(pixels, WIDTH, VRAM_HEIGHT))
