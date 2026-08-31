from worker import AbstractWorker
from connector.emulator import get_emulator_implementation
from common import logger
from game.entity import Entity


class UpdateEntity(AbstractWorker):
    def __init__(self, entity: Entity):
        super().__init__()
        self.entity = entity

    def run(
        self,
    ):
        self.working = True

        try:
            self.psx = get_emulator_implementation()(address="127.0.0.1", port=55355)
            self.psx.connect()

            logger.info(f"Updating entity at 0x{self.entity.address:08X}")
            self.psx.write_memory(self.entity.address, self.entity.to_bytearray())
        except Exception as exception:
            logger.error(exception)
        finally:
            self.psx.disconnect()

        logger.info("Finished updating entity")
        self.working = False
