# hydra_router/server/HydraServerPong.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

# !/usr/bin/env python

import argparse
import json
import sys
import time
from typing import Any, Dict

from hydra_router.constants.DHydra import DHydra, DHydraServerDef, DHydraServerMsg
from hydra_router.server.HydraServer import HydraServer
from hydra_router.utils.HydraMsg import HydraMsg


class HydraServerPong(HydraServer):
    """
    HydraServerPong implements a pong server that responds to structured ping messages
    using the HydraMsg protocol.
    """

    def __init__(
        self,
        address: str = "*",
        port: int = DHydraServerDef.PORT,
        response_delay: float = 0.0,
    ):
        """
        Initialize the HydraServerPong with pong-specific parameters.

        Args:
            address (str): The address to bind to (default: "*" for all interfaces)
            port (int): The port to bind to
            response_delay (float): Artificial delay before responding (for testing)
        """
        super().__init__(address=address, port=port, server_id="HydraPongServer")

        self.response_delay = response_delay
        self.ping_count = 0
        self.pong_count = 0

    def parse_ping_message(self, message_bytes: bytes) -> Dict[str, Any]:
        """
        Parse an incoming ping message.

        Attempts to decode and parse a JSON message from the client.
        If parsing fails, returns an error dictionary with the raw message.

        Args:
            message_bytes (bytes): Raw message from client

        Returns:
            Dict[str, Any]: Parsed ping message data or error information

        Raises:
            json.JSONDecodeError: If message is not valid JSON (caught and handled)
            UnicodeDecodeError: If message cannot be decoded as UTF-8 (caught
                and handled)
        """
        try:
            # For now, assume simple JSON message
            # In a full implementation, this would deserialize HydraMsg
            message_str = message_bytes.decode("utf-8")
            return json.loads(message_str)  # type: ignore
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.log.warning(f"Failed to parse ping message: {e}")
            return {
                "error": "Invalid message format",
                "raw": message_bytes.decode("utf-8", errors="replace"),
            }

    def create_pong_response(self, ping_data: Dict[str, Any]) -> HydraMsg:
        """
        Create a structured pong response using HydraMsg.

        Extracts information from the ping message and creates a corresponding
        pong response with original ping data and server response information.

        Args:
            ping_data (Dict[str, Any]): Parsed ping message data

        Returns:
            HydraMsg: Structured pong response message

        Raises:
            json.JSONDecodeError: If ping payload is not valid JSON (caught and handled)
        """
        # Extract ping information
        ping_payload = {}
        if "payload" in ping_data:
            try:
                ping_payload = json.loads(ping_data["payload"])
            except json.JSONDecodeError:
                ping_payload = {"message": ping_data.get("payload", "")}

        # Create pong response
        pong_payload = {
            "original_sequence": ping_payload.get("sequence", 0),
            "original_message": ping_payload.get("message", ""),
            "original_timestamp": ping_payload.get("timestamp", 0),
            "pong_message": "pong",
            "pong_timestamp": time.time(),
            "server_id": "HydraPongServer",
        }

        return HydraMsg(
            sender="HydraPongServer",
            target=ping_data.get("sender", "Unknown"),
            method="pong",
            payload=json.dumps(pong_payload),
        )

    def create_error_response(self, error_message: str) -> bytes:
        """
        Create an error response for invalid ping messages.

        Generates a standardized error response in JSON format with
        error details, server identification, and timestamp.

        Args:
            error_message (str): Description of the error

        Returns:
            bytes: Error response as JSON bytes
        """
        error_response = {
            "error": error_message,
            "server_id": "HydraPongServer",
            "timestamp": time.time(),
        }
        return json.dumps(error_response).encode("utf-8")

    def handle_message(self, message: bytes) -> bytes:
        """
        Handle incoming ping messages and generate pong responses.

        Processes incoming messages, validates them as ping requests,
        and generates appropriate pong responses or error messages.
        Updates internal counters and applies configured response delays.

        Args:
            message (bytes): The ping message received from a client

        Returns:
            bytes: The pong response to send back to the client

        Raises:
            Exception: If message processing fails (caught and handled)
        """
        self.ping_count += 1

        try:
            # Parse incoming ping message
            ping_data = self.parse_ping_message(message)

            if "error" in ping_data:
                self.log.error(f"Invalid ping message: {ping_data['error']}")
                return self.create_error_response(ping_data["error"])

            # Log ping details
            ping_method = ping_data.get("method", "unknown")
            ping_sender = ping_data.get("sender", "unknown")

            if ping_method == "ping":
                self.log.info(f"Received ping #{self.ping_count} from {ping_sender}")

                # Add artificial delay if configured
                if self.response_delay > 0:
                    time.sleep(self.response_delay)

                # Create pong response
                pong_msg = self.create_pong_response(ping_data)

                # Serialize pong response
                # (in full implementation, use HydraMsg serialization)
                pong_data = {
                    "sender": pong_msg._sender,
                    "target": pong_msg._target,
                    "method": pong_msg._method,
                    "payload": pong_msg._payload,
                    "id": str(pong_msg._id),
                }

                pong_bytes = json.dumps(pong_data).encode("utf-8")
                self.pong_count += 1

                self.log.info(f"Sending pong #{self.pong_count} to {ping_sender}")
                return pong_bytes

            else:
                error_msg = f"Unsupported method: {ping_method}"
                self.log.warning(error_msg)
                return self.create_error_response(error_msg)

        except Exception as e:
            error_msg = f"Failed to process ping message: {e}"
            self.log.error(error_msg)
            return self.create_error_response(error_msg)

    def run(self) -> None:
        """
        Run the pong server, listening for ping messages and responding with pongs.

        Starts the server and begins listening for incoming ping messages.
        Logs server startup information and handles keyboard interruption gracefully.
        Displays a summary of processed messages when shutting down.

        Returns:
            None

        Raises:
            KeyboardInterrupt: When user interrupts with Ctrl+C (caught and handled)
        """
        self.log.info(f"Starting pong server on {self.address}:{self.port}")
        if self.response_delay > 0:
            self.log.info(f"Artificial response delay: {self.response_delay}s")

        try:
            self.start()
        except KeyboardInterrupt:
            self.log.info("Pong server interrupted by user")
        finally:
            # Print summary
            self.log.info(
                f"Server summary: {self.pong_count} pongs sent for "
                f"{self.ping_count} pings received"
            )


def main() -> None:
    """
    Main entry point for hydra-pong-server command.

    Parses command line arguments, creates a HydraServerPong instance,
    and runs the pong server. Handles keyboard interruption and errors
    gracefully with appropriate exit codes.

    Returns:
        None

    Raises:
        KeyboardInterrupt: When user interrupts with Ctrl+C (handled)
        Exception: For any other errors during execution (handled)
    """
    parser = argparse.ArgumentParser(
        description="HydraRouter Pong Server - Respond to structured ping messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hydra-pong-server                          # Start server on default (*:5757)
  hydra-pong-server --port 8080              # Start server on port 8080
  hydra-pong-server --address localhost      # Start server on localhost:5757
  hydra-pong-server --address 0.0.0.0 --port 9000  # Start on all interfaces
  hydra-pong-server --delay 0.1              # Add 100ms response delay
        """,
    )

    parser.add_argument(
        "--address",
        "-a",
        default="*",
        help=DHydraServerMsg.ADDRESS_HELP,
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DHydraServerDef.PORT,
        help=DHydraServerMsg.PORT_HELP.format(port=DHydraServerDef.PORT),
    )

    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=0.0,
        help="Artificial delay before responding to pings in seconds (default: 0.0)",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"hydra-pong-server {DHydra.VERSION}",
    )

    args = parser.parse_args()

    try:
        print(DHydraServerMsg.STARTING.format(address=args.address, port=args.port))
        print(DHydraServerMsg.STOP_HELP)

        server = HydraServerPong(
            address=args.address, port=args.port, response_delay=args.delay
        )
        server.run()

    except KeyboardInterrupt:
        print(DHydraServerMsg.USER_STOP)
        sys.exit(0)
    except Exception as e:
        print(DHydraServerMsg.ERROR.format(e=e))
        sys.exit(1)


if __name__ == "__main__":
    main()
