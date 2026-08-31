from worker import AbstractWorker
from signals import VRAMSignals
from connector.emulator import get_emulator_implementation
from common import logger
from game.vram import Pixel, Pixels, VRAM_HEIGHT


def get_pixel(value: int, inverted: bool = False) -> Pixel:
    red = (value >> 0) & 0x1F
    green = (value >> 5) & 0x1F
    blue = (value >> 10) & 0x1F
    alpha = (value >> 15) & 0x01

    red = (red * 255) // 31
    green = (green * 255) // 31
    blue = (blue * 255) // 31
    alpha = (1 - alpha) * 255

    if inverted:
        red = 255 - red
        green = 255 - green
        blue = 255 - blue

    return Pixel(red, green, blue, alpha)


class VRAMWorker(AbstractWorker):
    signals: VRAMSignals

    def __init__(self):
        super().__init__()
        self.signals = VRAMSignals()

    def run(self):
        self.working = True

        try:
            self.psx = get_emulator_implementation()(address="127.0.0.1", port=55355)
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
        for y in range(VRAM_HEIGHT):
            data = self.psx.read_memory(WIDTH * y, size=WIDTH, domain="GPURAM")
            for byte in data:
                pixels.append(get_pixel(byte))

        self.signals.vram_loaded.emit(Pixels(pixels, WIDTH, VRAM_HEIGHT))
