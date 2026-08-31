import time
from enum import Enum

from common import logger


class EmulatorException(Exception):
    pass


class EmulatorDisconnectError(EmulatorException):
    pass


class InvalidEmulatorStateError(EmulatorException):
    pass


class BadEmulatorResponse(EmulatorException):
    pass


class EmulatorStatus(Enum):
    UNKNOWN = 1
    PAUSED = 2
    PLAYING = 3
    CONTENTLESS = 3


CORE_TYPE = "playstation"


class MemoryBank:
    address: int
    size: int
    data: bytearray

    def __init__(self, address: int, data: bytearray):
        self.address = address
        self.size = len(data)
        self.data = data

    def read(self, address: int, size: int = 1) -> bytearray | None:
        if address < self.address or address + size > self.address + self.size:
            return None

        offset = address - self.address
        return self.data[offset : offset + size]


class Emulator:
    name: str = "Emulator"

    cache: list[MemoryBank] = []
    connected: bool

    def __init__(self, address, port) -> None:
        self.connected = False

        self.address = address
        self.port = port

    def write_memory(self, address, bytes: bytearray | bytes):
        """Abstract"""
        pass

    def _read_memory(self, address, size=1):
        """Abstract"""
        return bytearray(1)

    def disconnect(self):
        """Abstract"""
        pass

    def get_version(self):
        """Abstract"""
        return ""

    def get_status(self):
        """Abstract"""
        return (EmulatorStatus.UNKNOWN, "", "", "")

    def connect(self, timeout: float = 5):
        logger.info(f"Connecting to {self.name}...")

        start_time = time.time()
        timeout = 5.0

        self.connected = False
        while not self.connected and time.time() - start_time < timeout / 1000.0:
            try:
                version = self.get_version()
                status, core_type, rom_name, _ = self.get_status()
                if (
                    status == EmulatorStatus.PAUSED or status == EmulatorStatus.PLAYING
                ) and core_type == CORE_TYPE:
                    self.connected = True
                    break
            except (BlockingIOError, TimeoutError, ConnectionResetError):
                pass

            time.sleep(0.5)

        if self.connected:
            logger.info(
                f"Connected to {self.name} version {version} running {rom_name}"
            )
        else:
            logger.error("Unable to connect to RetroArch")

    def create_cache(self, address: int, size: int = 1):
        """Put a memory bank in cache
        Any operation landing in that range will read value from cache"""
        data = self.read_memory_block(address, size)
        self.cache.append(MemoryBank(address, data))

    def destroy_cache(self):
        self.cache = []

    def read_memory(self, address: int, size: int = 1) -> bytearray:
        """Performs a cached read"""
        for memory_bank in self.cache:
            data = memory_bank.read(address, size)

            if data is not None:
                return data

        return self._read_memory(address, size)

    def read_memory_block(self, address: int, size: int) -> bytearray:
        block = bytearray()
        remaining_size = size
        while remaining_size:
            chunk = self.read_memory(address + len(block), remaining_size)
            remaining_size -= len(chunk)
            block += chunk

        return block
