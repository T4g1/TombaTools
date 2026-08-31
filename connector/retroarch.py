import re
from PySide6.QtNetwork import QUdpSocket, QHostAddress
from PySide6.QtCore import Slot, QByteArray

from connector.emulator import Emulator, BadEmulatorResponse, EmulatorStatus
from common import logger


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


class RetroArch(Emulator):
    name: str = "RetroArch"

    def __init__(self, address, port, socket: QUdpSocket) -> None:
        super().__init__(address=address, port=port)

        self.socket = socket

        self.socket.errorOccurred.connect(self.socket_error)

    @Slot(QUdpSocket.SocketError)
    def socket_error(self, error):
        logger.error(f"{error} - {self.socket.errorString()}")

    def disconnect(self):
        self.socket.close()

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

    def sanitize_address(self, address: int) -> int:
        """RetroArch does not handle 0x8XXXXXXX addresses"""
        return address & 0x7FFFFFFF
