# hydra_router/server/HydraServer.py
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

from hydra_router.constants.DHydra import DHydraServerDef, DHydraServerMsg
from hydra_router.utils.HydraLog import HydraLog


class HydraServer(ABC):
    """
    Abstract base class for HydraServer implementations.

    Provides common ZeroMQ-based server functionality that binds to a port
    and handles client requests using the REQ/REP pattern. Subclasses must
    implement application-specific message handling logic.
    """

    def __init__(
        self,
        address: str = "*",
        port: int = DHydraServerDef.PORT,
        server_id: Optional[str] = None,
    ):
        """
        Initialize the HydraServer with binding parameters.

        Args:
            address (str): The address to bind to (default: "*" for all interfaces)
            port (int): The port to bind to
            server_id (str): Identifier for logging purposes
        """
        self.log = HydraLog(client_id=server_id or "HydraServer", to_console=True)

        self.address = address
        self.port = port
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None

    def _setup_socket(self) -> None:
        """
        Set up ZeroMQ context and REP socket.

        Creates a new ZeroMQ context and REP socket, then binds to the
        configured address and port. Logs binding success or exits on failure.

        Returns:
            None

        Raises:
            Exception: If socket creation or binding fails
        """
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REP)
            bind_address = f"tcp://{self.address}:{self.port}"
            self.socket.bind(bind_address)
            self.log.info(DHydraServerMsg.BIND.format(bind_address=bind_address))
        except Exception as e:
            self.log.error(DHydraServerMsg.ERROR.format(e=e))
            exit(1)

    def start(self) -> None:
        """
        Start the server and begin listening for requests in a continuous loop.

        Initializes the socket if needed, then enters an infinite loop waiting
        for client requests. Each received message is processed by the
        handle_message() method and the response is sent back to the client.
        The loop continues until interrupted by Ctrl+C or an exception occurs.

        Returns:
            None

        Raises:
            KeyboardInterrupt: When user interrupts with Ctrl+C
            RuntimeError: If socket is not initialized
            Exception: If message handling fails
        """
        if self.socket is None:
            self._setup_socket()

        self.log.info(
            DHydraServerMsg.LOOP_UP.format(address=self.address, port=self.port)
        )

        try:
            while True:
                # Wait for next request from client
                if self.socket is not None:
                    message = self.socket.recv()
                    self.log.debug(DHydraServerMsg.RECEIVE.format(message=message))

                    # Process message using subclass implementation
                    response = self.handle_message(message)

                    # Send reply back to client
                    self.socket.send(response)
                    self.log.debug(DHydraServerMsg.SENT.format(response=response))
                else:
                    raise RuntimeError("Socket not initialized")

        except KeyboardInterrupt:
            self.log.info(DHydraServerMsg.SHUTDOWN)
        except Exception as e:
            self.log.error(DHydraServerMsg.ERROR.format(e=e))
            exit(1)
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """
        Clean up ZeroMQ resources.

        Properly closes the socket and terminates the ZeroMQ context
        to prevent resource leaks. Should be called when the server
        is shutting down.

        Returns:
            None
        """
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        self.log.info(DHydraServerMsg.CLEANUP)

    @abstractmethod
    def handle_message(self, message: bytes) -> bytes:
        """
        Abstract method that subclasses must implement to define
        application-specific message handling logic.

        Args:
            message (bytes): The message received from a client

        Returns:
            bytes: The response to send back to the client
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
        Abstract method that subclasses must implement to define
        application-specific server startup behavior.
        """
        pass
