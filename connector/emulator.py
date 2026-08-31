import re
import time
from enum import Enum
from PySide6.QtNetwork import QUdpSocket, QHostAddress
from PySide6.QtCore import Slot, QByteArray

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


def status_from_string(value):
    match value:
        case "PAUSED":
            return EmulatorStatus.PAUSED
        case "PLAYING":
            return EmulatorStatus.PLAYING
        case "CONTENTLESS":
            return EmulatorStatus.CONTENTLESS
        case _:
            return EmulatorStatus.UNKNOWN


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
    name: str = "RetroArch"

    cache: list[MemoryBank] = []
    socket: QUdpSocket
    connected: bool

    def __init__(self, address, port, socket: QUdpSocket) -> None:
        self.connected = False

        self.address = address
        self.port = port
        self.socket = socket

        self.socket.errorOccurred.connect(self.socket_error)

    @Slot(QUdpSocket.SocketError)
    def socket_error(self, error):
        logger.error(f"{error} - {self.socket.errorString()}")

    def connect(self, timeout: float = 5):
        logger.info("Connecting to RetroArch...")

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

    def disconnect(self):
        self.socket.close()

    def send(self, b):
        if type(b) is str:
            b = b.encode("ascii")
        # logger.debug(f"> {b}")
        self.socket.writeDatagram(b, QHostAddress(self.address), self.port)

    def recv(self, timeout_ms: int = 15000) -> bytes:
        if not self.socket.hasPendingDatagrams():
            if not self.socket.waitForReadyRead(timeout_ms):
                logger.error("Timeout error while receiving data")
                return b""

        buffer = QByteArray()
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            data = datagram.data()
            # logger.debug(f"< {data}")
            buffer.append(data)

        return bytes(buffer.data())

    def send_command(self, command):
        self.send(f"{command}\n")
        response_str = self.recv()
        self.check_command_response(command, response_str)
        return response_str.rstrip()

    def check_command_response(self, command: str, response: bytes):
        if command == "VERSION":
            ok = re.match(r"\d+\.\d+\.\d+", response.decode("ascii")) is not None
        else:
            ok = response.startswith(command.encode())
        if not ok:
            raise BadEmulatorResponse(f"Bad response to command {command} - {response}")

    def get_version(self):
        version = self.send_command("VERSION")
        return version.decode("ascii", errors="replace")

    def get_status(self):
        status = self.send_command("GET_STATUS")
        if status.count(b" ") < 2:
            return (EmulatorStatus.UNKNOWN, "", "", "")

        _, status, info = status.split(b" ", 2)
        status = status_from_string(status.decode("ascii", errors="replace"))

        if info.count(b",") < 2:
            return (status, "", "", "")

        core_type, rom_name, rom_crc = info.split(b",", 2)

        return (
            status,
            core_type.decode("ascii", errors="replace"),
            rom_name.decode("ascii", errors="replace"),
            rom_crc,
        )

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

    def sanitize_address(self, address: int) -> int:
        """RetroArch does not handle 0x8XXXXXXX addresses"""
        return address & 0x7FFFFFFF

    def write_memory(self, address, bytes: bytearray | bytes):
        command = "WRITE_CORE_MEMORY"

        address = self.sanitize_address(address)

        self.send(f'{command} {hex(address)} {" ".join(hex(b) for b in bytes)}')
        response = self.recv()
        self.check_command_response(command, response)
        splits = response.decode().split(" ", 3)

        assert splits[0] == command

        if splits[2] == "-1":
            logger.info(splits[3])

    def _read_memory(self, address, size=1):
        command = "READ_CORE_MEMORY"

        address = self.sanitize_address(address)

        self.send(f"{command} {hex(address)} {size}\n")
        response = self.recv()
        self.check_command_response(command, response)
        splits = response.decode().split(" ", 2)
        try:
            response_addr = int(splits[1], 16)
        except ValueError:
            raise BadEmulatorResponse(f"Cannot convert {splits[1]} to hexadecimal")

        if response_addr != address:
            raise BadEmulatorResponse(
                f"Bad response address: 0x{response_addr:08X} instead of 0x{address:08X}"
            )

        try:
            ret = bytearray.fromhex(splits[2])
            if len(ret) > size:
                raise BadEmulatorResponse()
            return ret
        except ValueError:
            raise BadEmulatorResponse(
                f"Unexpected response to {command} on 0x{address:08X} for {size} bytes: {response}"
            )

    def read_memory_block(self, address: int, size: int) -> bytearray:
        block = bytearray()
        remaining_size = size
        while remaining_size:
            chunk = self.read_memory(address + len(block), remaining_size)
            remaining_size -= len(chunk)
            block += chunk

        return block
