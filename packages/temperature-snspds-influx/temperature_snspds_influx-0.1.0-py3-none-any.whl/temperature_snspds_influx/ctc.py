# Copyright (c) 2026 Yoann Piétri
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Interface for the CTC100 temperature controller.
"""

import abc
import time
import socket

import serial


class CTC100(abc.ABC):
    """CTC100 interface class."""

    address: str  #: Address used for the connection.
    precision: int  #: Requested number of digits.

    def __init__(self, address: str, precision: int):
        """
        Args:
            address (str): address (com port, tty or ip_address:port) to connect to.
            precision (int): number of digits wanted in the answer from the CTC.

        Raises:
            ValueError: if the precision is not an int or not between 0 and 6.
        """
        self.address = address
        if precision == int(precision) and 0 <= precision <= 6:
            self.precision = precision
        else:
            raise ValueError(
                "Precision parameter must be an int between 0 and 6 included."
            )

    @abc.abstractmethod
    def open(self):
        """Open the CTC connection."""

    @abc.abstractmethod
    def close(self):
        """Close the CTC connection."""

    @abc.abstractmethod
    def get_channel(self, channel: str) -> float:
        """Get the value of the channel `channel`.

        Args:
            channel (str): identifier of the channel.

        Returns:
            float: current value of the channel.
        """


class USBCTC100(CTC100):
    """Serial interface for the CTC100."""

    device: serial.Serial | None = None  #: Serial connection.

    SLEEP_TIME: float = (
        0.05  #: Sleep time between sending a command and reading the answer.
    )

    def open(self) -> None:
        self.device = serial.Serial(self.address)

    def close(self) -> None:
        if self.device is not None:
            self.device.close()
        self.device = None

    def _read_serial(self) -> str:
        if self.device is None:
            raise IOError("Cannot read serial on a closed device.")
        response = b""
        x = self.device.read()
        while x != b"\n":
            response += x
            x = self.device.read()
        # Remove the \r
        return response[:-1].decode()

    def _write_serial(self, message: str) -> int:
        if self.device is None:
            raise IOError("Cannot write serial on a close device.")
        return self.device.write(str(message + "\r\n").encode())

    def _query_serial(self, message: str) -> str:
        self._write_serial(message)
        time.sleep(self.SLEEP_TIME)
        return self._read_serial()

    def get_channel(self, channel: str) -> float:
        res = self._query_serial(f"{channel}.value?")
        return float(res.split(" = ")[1])


class EthernetCTC100(CTC100):
    """Ethernet connection for the CTC.

    The address parameter must be in the format ip_adress:port
    """

    ip_address: str  #: IP address to connect to.
    port: int  #: Port to connect to.
    conn: socket.socket | None  #: Socket connection.

    TIMEOUT = 2  #: Timeout of the socket connection.
    BUFFER_SIZE = 4096  #: Buffer in bytes of the socket connection.

    def __init__(self, address: str, precision: int):
        super().__init__(address, precision)
        self.ip_address, port = self.address.split(":")
        self.port = int(port)
        self.conn = None

    def open(self):
        self.conn = socket.create_connection(
            (self.ip_address, self.port), timeout=self.TIMEOUT
        )

    def close(self):
        if self.conn:
            self.conn.close()
        self.conn = None

    def _send_command(self, command: str) -> None:
        if self.conn is None:
            raise IOError("Cannot send command on a closed connection.")
        self.conn.sendall((command + "\n").encode("ascii"))

    def _query(self, command: str) -> str:
        if self.conn is None:
            raise IOError("Cannot query on a closed connection.")
        self._send_command(command)
        return self.conn.recv(self.BUFFER_SIZE).decode("ascii").strip()

    def get_channel(self, channel: str) -> float:
        res = self._query(f"{channel}.value?")
        return float(res.split(" = ")[1])
