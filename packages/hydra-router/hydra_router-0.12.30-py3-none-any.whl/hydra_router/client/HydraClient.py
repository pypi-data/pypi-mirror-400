# hydra_router/client/HydraClient.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

from abc import ABC, abstractmethod
from typing import Optional

import zmq

from hydra_router.constants.DHydra import DHydraMsg, DHydraServerDef
from hydra_router.utils.HydraLog import HydraLog


class HydraClient(ABC):
    """
    Abstract base class for HydraClient implementations.

    Provides common ZeroMQ-based client functionality that connects to a server
    and sends requests using the REQ/REP pattern. Subclasses must implement
    application-specific message handling logic.
    """

    def __init__(
        self,
        server_hostname: Optional[str] = None,
        server_port: Optional[int] = None,
        client_id: Optional[str] = None,
    ) -> None:
        """
        Initialize the HydraClient with server connection parameters.

        Args:
            server_hostname (str): The server hostname to connect to
            server_port (int): The server port to connect to
            client_id (str): Identifier for logging purposes
        """
        self.log = HydraLog(client_id=client_id or "HydraClient", to_console=True)

        self._server_hostname = server_hostname or DHydraServerDef.HOSTNAME
        self._server_port = server_port or DHydraServerDef.PORT

        self.server_address = (
            "tcp://" + self._server_hostname + ":" + str(self._server_port)
        )
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self._setup_socket()

    def _setup_socket(self) -> None:
        """
        Set up ZeroMQ context and REQ socket with connection.

        Creates a new ZeroMQ context and REQ socket, then connects to the
        configured server address. Logs connection success or exits on failure.

        Returns:
            None

        Raises:
            Exception: If socket creation or connection fails
        """
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.server_address)
            self.log.info(
                DHydraMsg.CONNECTED.format(server_address=self.server_address)
            )
        except Exception as e:
            self.log.error(DHydraMsg.ERROR.format(e=e))
            exit(1)

    def send_message(self, message: bytes) -> bytes:
        """
        Send a message to the server and wait for response.

        Sends a message to the connected server using the REQ/REP pattern
        and blocks until a response is received. Logs the message exchange
        for debugging purposes.

        Args:
            message (bytes): The message to send to the server

        Returns:
            bytes: The response received from the server

        Raises:
            RuntimeError: If socket is not initialized
            Exception: If message sending or receiving fails
        """
        try:
            self.log.debug(DHydraMsg.SENDING.format(message=message))
            if self.socket is not None:
                self.socket.send(message)

                # Wait for response
                response: bytes = self.socket.recv()
                self.log.debug(DHydraMsg.RECEIVED.format(response=response))
                return response
            else:
                raise RuntimeError("Socket not initialized")

        except Exception as e:
            self.log.error(DHydraMsg.ERROR.format(e=e))
            exit(1)

    def _cleanup(self) -> None:
        """
        Clean up ZeroMQ resources.

        Properly closes the socket and terminates the ZeroMQ context
        to prevent resource leaks. Should be called when the client
        is no longer needed.

        Returns:
            None
        """
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        self.log.info(DHydraMsg.CLEANUP)

    @abstractmethod
    def run(self) -> None:
        """
        Abstract method that subclasses must implement to define
        application-specific client behavior.
        """
        pass
