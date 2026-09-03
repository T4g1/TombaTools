from PySide6.QtCore import QObject, QTimer, Signal, Slot

from connector.emulator import Emulator, get_emulator_implementation
from common import logger
from game.vram import VRAM_HEIGHT, BYTES_PER_LINE
from game.frame import Frame
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
    preview_clear = Signal()
    preview_frames = Signal(list)

    psx: Emulator

    def __init__(self, address="127.0.0.1", port=55355):
        super().__init__()
        self.address = address
        self.port = port

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.ping)

    @Slot()
    def connect(self):
        self.psx = get_emulator_implementation()(address=self.address, port=self.port)
        self.psx.connect()
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

    @Slot(Entity)
    def load_preview(self, entity: Entity):
        logger.info(f"Loading preview for entity at 0x{entity.address:08X}...")

        self.preview_clear.emit()

        logger.info(f"Frame array: 0x{entity.frame_array:08X}")
        logger.info(f"Current frame: 0x{entity.current_frame:08X}")

        if entity.frame_array == 0:
            return

        if entity.current_frame == 0:
            return

        animation_data = self.psx.read_memory(entity.current_frame, 4)
        logger.info(f"Animation data: 0x{animation_data.hex()}")
        animation_index = animation_data[0] * 4

        frame_index_address = entity.frame_array + animation_index
        logger.info(f"Frame index address: 0x{frame_index_address:08X}")
        frame_index_data = self.psx.read_memory(frame_index_address, 4)
        logger.info(f"Frame index data: 0x{frame_index_data.hex()}")
        frame_count = int.from_bytes(frame_index_data[0:2], byteorder="little")
        frame_index = int.from_bytes(frame_index_data[2:4], byteorder="little")
        logger.info(f"Frame count: {frame_count}")
        logger.info(f"Frame index: 0x{frame_index:04X}")

        frames: list[Frame] = []
        for i in range(frame_count):
            frame_address = entity.frame_array + frame_index + (0x10 * i)
            logger.info(f"Frame {i} address: 0x{frame_address:08X}")

            if frame_address == 0:
                return

            raw_frame = self.psx.read_memory(frame_address, 16)
            logger.info(f"Frame: 0x{raw_frame.hex()}")

            logger.info(f"Entity VRAM page offset: {entity.vram_page_offset}")
            frame = Frame(raw_frame, entity.vram_page_offset)
            logger.info(f"{frame}")

            frames.append(frame)

        self.preview_frames.emit(frames)

        logger.info("Preview loaded")

    @Slot()
    def load_entities(self):
        logger.info("Loading entities...")
        self.load_game_entities()
        self.load_event_cube()
        self.load_object_slots()
        logger.info("Finished loading entitiePs")

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
