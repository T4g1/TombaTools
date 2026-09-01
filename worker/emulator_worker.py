from PySide6.QtCore import QObject, QTimer, Signal, Slot

from connector.emulator import Emulator, get_emulator_implementation
from common import logger
from game.vram import VRAM_HEIGHT, BYTES_PER_LINE
from game.entity import (
    Entity,
    GAME_ENTITY_ADDRESS,
    GAME_ENTITY_COUNT,
    OBJECT_SLOTS_ADDRESS,
    OBJECT_SLOTS_COUNT,
    EVENT_CHAR_ADDRESS,
    EVENT_CHAR_COUNT,
)


class EmulatorWorker(QObject):
    connected = Signal()
    vram_loaded = Signal(bytearray)
    entity_loaded = Signal(Entity)

    psx: Emulator

    def __init__(self, address="127.0.0.1", port=55355):
        super().__init__()
        self.address = address
        self.port = port
        self.timer = None

    @Slot()
    def connect(self):
        self.psx = get_emulator_implementation()(address=self.address, port=self.port)
        self.psx.connect()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.ping)
        self.timer.start(4000)

        self.connected.emit()

    @Slot()
    def ping(self):
        if not self.psx:
            return

        try:
            self.psx.ping()
        except Exception as exception:
            logger.error(exception)

    @Slot()
    def load_entities(self):
        logger.info("Loading entities...")
        self.load_game_entities()
        self.load_event_cube()
        self.load_object_slots()
        logger.info("Finished loading entities")

    def _load_entities(
        self,
        address: int,
        count: int,
        type: int | None = None,
        size: int = Entity.SIZE,
        is_occupied: bool | None = None,
    ) -> list[Entity]:
        entities = []
        for _ in range(count):
            address = address + size
            entity_raw = self.psx.read_memory_block(address, size)
            entity = Entity(address)
            entity.load(entity_raw)

            if (entity.type == type or type is None) and (
                entity.occupied != 0x00 or not is_occupied or is_occupied is None
            ):
                self.entity_loaded.emit(entity)

        return entities

    def load_game_entities(self) -> list[Entity]:
        return self._load_entities(GAME_ENTITY_ADDRESS, GAME_ENTITY_COUNT)

    def load_event_cube(self) -> list[Entity]:
        return self._load_entities(EVENT_CHAR_ADDRESS, EVENT_CHAR_COUNT)

    def load_object_slots(self) -> list[Entity]:
        return self._load_entities(OBJECT_SLOTS_ADDRESS, OBJECT_SLOTS_COUNT)

    @Slot()
    def load_vram(self):
        try:
            logger.info("Loading VRAM...")
            self._load_vram()
        except Exception as exception:
            logger.error(exception)

        logger.info("Finished loading VRAM")

    def _load_vram(self):
        factor = 2
        data: bytearray = bytearray()

        for y in range(VRAM_HEIGHT // factor):
            data += self.psx.read_memory(
                BYTES_PER_LINE * y * factor,
                size=BYTES_PER_LINE * factor,
                domain="GPURAM",
            )

        self.vram_loaded.emit(data)

    @Slot(object)
    def update_entity(self, entity: Entity):
        if not self.psx:
            return

        try:
            logger.info(f"Updating entity at 0x{entity.address:08X}")
            self.psx.write_memory(entity.address, entity.to_bytearray())
        except Exception as exception:
            logger.error(exception)

        logger.info("Finished updating entity")
