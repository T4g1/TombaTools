import enum
import base64
import json
from typing import Any

from PySide6.QtNetwork import QTcpSocket

from connector.emulator import (
    Emulator,
    InvalidEmulatorStateError,
    EmulatorStatus,
    BadEmulatorResponse,
    CORE_TYPE,
)

# from common import logger

BIZHAWK_SOCKET_PORT_RANGE_START = 43055
BIZHAWK_SOCKET_PORT_RANGE_SIZE = 5


class ConnectionStatus(enum.IntEnum):
    NOT_CONNECTED = 1
    TENTATIVE = 2
    CONNECTED = 3


class BizHawk(Emulator):
    socket: QTcpSocket

    connection_status: ConnectionStatus

    def __init__(self, address, port):
        super().__init__(address=address, port=port)

        self.connection_status = ConnectionStatus.NOT_CONNECTED
        self.socket = QTcpSocket()

    def prepare(self, timeout_ms: int = 1000) -> bool:
        rotation_steps = (
            0 if self.port is None else self.port - BIZHAWK_SOCKET_PORT_RANGE_START
        )

        ports = [
            *range(
                BIZHAWK_SOCKET_PORT_RANGE_START,
                BIZHAWK_SOCKET_PORT_RANGE_START + BIZHAWK_SOCKET_PORT_RANGE_SIZE,
            )
        ]
        ports = ports[rotation_steps:] + ports[:rotation_steps]

        for port in ports:
            try:
                self.socket.connectToHost(self.address, port)
                self.connection_status = ConnectionStatus.TENTATIVE

                if self.socket.waitForConnected(timeout_ms):
                    return True
            except (TimeoutError, ConnectionRefusedError):
                continue

        return False

    def _send_message(self, message: str, timeout_ms: int = 3000) -> str:
        try:
            # logger.info(f"> {message.encode("utf-8")}")
            self.socket.write(message.encode("utf-8") + b"\n")
            if not self.socket.waitForReadyRead(msecs=timeout_ms):
                raise InvalidEmulatorStateError(f"Time out with command: {message}")

            response = bytearray(self.socket.readAll().data())
            # logger.info(f"< {response.decode("utf-8")}")

            if response == b"":
                self.connected = False
                raise InvalidEmulatorStateError("Connection closed")

            if self.connection_status == ConnectionStatus.TENTATIVE:
                self.connection_status = ConnectionStatus.CONNECTED

            return response.decode("utf-8")
        except Exception:
            self.connected = False
            raise InvalidEmulatorStateError("Connection reset")

    def send_requests(self, requests: list[dict[str, Any]]):
        responses = json.loads(self._send_message(json.dumps(requests)))

        errors: list[BadEmulatorResponse] = []
        for response in responses:
            if response["type"] == "ERROR":
                errors.append(BadEmulatorResponse(response["err"]))

        if errors:
            raise InvalidEmulatorStateError("Connector script returned errors", errors)

        return responses

    def send_command(self, command: str) -> bytearray:
        self.socket.write(bytearray(command, "utf-8"))
        return bytearray(self.socket.readAll().data())

    def get_system(self) -> str:
        """Gets the system name for the currently loaded ROM"""
        response = (self.send_requests([{"type": "SYSTEM"}]))[0]

        if response["type"] != "SYSTEM_RESPONSE":
            raise BadEmulatorResponse(
                f"Expected response of type SYSTEM_RESPONSE but got {response['type']}"
            )

        return response["value"]

    def get_version(self):
        try:
            return int(self._send_message("VERSION"))
        except Exception:
            raise BadEmulatorResponse("BizHawk: Unable to get version")

    def get_hash(self) -> str:
        """Gets the hash value of the currently loaded ROM"""
        response = self.send_requests([{"type": "HASH"}])[0]

        if response["type"] != "HASH_RESPONSE":
            raise BadEmulatorResponse(
                f"Expected response of type HASH_RESPONSE but got {response['type']}"
            )

        return response["value"]

    def get_status(self):
        try:
            core_type = self.get_system()
            rom_crc = self.get_hash()

            status = EmulatorStatus.UNKNOWN
            if self.connection_status is ConnectionStatus.CONNECTED:
                if rom_crc != "":
                    status = EmulatorStatus.PLAYING
                else:
                    status = EmulatorStatus.CONTENTLESS

            if core_type == "PSX":
                core_type = CORE_TYPE

            return (
                status,
                core_type,
                "?",
                rom_crc,
            )
        except Exception:
            raise InvalidEmulatorStateError("BizHawk: Unable to get status")

    def ping(self) -> None:
        """Sends a PING request and receives a PONG response."""
        response = (self.send_requests([{"type": "PING"}]))[0]

        if response["type"] != "PONG":
            raise BadEmulatorResponse(
                f"Expected response of type PONG but got {response['type']}"
            )

    def write_memory(self, address, bytes: bytearray | bytes, domain: str = ""):
        response = self.send_requests(
            [
                {
                    "type": "WRITE",
                    "address": address,
                    "value": base64.b64encode(bytes).decode("ascii"),
                    "domain": domain,
                }
            ]
        )

        for item in response:
            if item["type"] != "WRITE_RESPONSE":
                raise BadEmulatorResponse(
                    f"Expected response of type WRITE_RESPONSE or GUARD_RESPONSE but got {item['type']}"
                )

        return True

    def _read_memory(self, address: int, size: int = 1, domain: str = "") -> bytearray:
        response = self.send_requests(
            [{"type": "READ", "address": address, "size": size, "domain": domain}]
        )

        result: list[bytes] = []
        for item in response:
            if item["type"] != "READ_RESPONSE":
                raise BadEmulatorResponse(
                    f"Expected response of type READ_RESPONSE or GUARD_RESPONSE but got {item['type']}"
                )

            result.append(base64.b64decode(item["value"]))

        return bytearray(b"".join(result))
