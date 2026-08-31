from PySide6.QtNetwork import QUdpSocket

from worker import AbstractWorker
from connector.retroarch import RetroArch
from common import logger
from game.entity import (
    Entity,
    GAME_ENTITY_ADDRESS,
    GAME_ENTITY_COUNT,
    OBJECT_SLOTS_ADDRESS,
    OBJECT_SLOTS_COUNT,
    EVENT_CHAR_ADDRESS,
    EVENT_CHAR_COUNT,
)


class DiscoverEntityWorker(AbstractWorker):
    def run(self):
        self.working = True

        try:
            socket = QUdpSocket()
            self.psx = RetroArch(address="127.0.0.1", port=55355, socket=socket)
            self.psx.connect()

            logger.info("Loading entities...")
            self.load_entities()
            self.load_event_cube()
            self.load_object_slots()
        except Exception as exception:
            logger.error(exception)
        finally:
            self.psx.disconnect()

        if not self.working:
            return

        logger.info("Finished loading entities")
        self.working = False

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
            if not self.working:
                break

            address = address + size
            entity_raw = self.psx.read_memory_block(address, size)
            entity = Entity(address)
            entity.load(entity_raw)

            if (entity.type == type or type is None) and (
                entity.occupied != 0x00 or not is_occupied or is_occupied is None
            ):
                self.signals.entity_discovered.emit(entity)

        return entities

    def load_entities(self) -> list[Entity]:
        return self._load_entities(GAME_ENTITY_ADDRESS, GAME_ENTITY_COUNT)

    def load_event_cube(self) -> list[Entity]:
        return self._load_entities(EVENT_CHAR_ADDRESS, EVENT_CHAR_COUNT)

    def load_object_slots(self) -> list[Entity]:
        return self._load_entities(OBJECT_SLOTS_ADDRESS, OBJECT_SLOTS_COUNT)
