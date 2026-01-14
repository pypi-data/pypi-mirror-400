# hydra_router/client/HydraClientPing.py
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
from typing import Any, Dict, Optional

from hydra_router.client.HydraClient import HydraClient
from hydra_router.constants.DHydra import DHydra, DHydraServerDef
from hydra_router.utils.HydraMsg import HydraMsg


class HydraClientPing(HydraClient):
    """
    HydraClientPing implements a ping client that sends structured ping messages
    to a pong server using the HydraMsg protocol.
    """

    def __init__(
        self,
        server_hostname: Optional[str] = None,
        server_port: Optional[int] = None,
        ping_count: int = 1,
        ping_interval: float = 1.0,
        message_payload: str = "ping",
    ) -> None:
        """
        Initialize the HydraClientPing with ping-specific parameters.

        Args:
            server_hostname (str): The server hostname to connect to
            server_port (int): The server port to connect to
            ping_count (int): Number of ping messages to send
            ping_interval (float): Interval between pings in seconds
            message_payload (str): Custom payload for ping messages
        """
        super().__init__(
            server_hostname=server_hostname,
            server_port=server_port,
            client_id="HydraPingClient",
        )

        self.ping_count = ping_count
        self.ping_interval = ping_interval
        self.message_payload = message_payload
        self.sent_pings = 0
        self.received_pongs = 0

    def create_ping_message(self, sequence: int) -> HydraMsg:
        """
        Create a structured ping message using HydraMsg.

        Args:
            sequence (int): Sequence number for the ping

        Returns:
            HydraMsg: Structured ping message
        """
        return HydraMsg(
            sender="HydraPingClient",
            target="HydraPongServer",
            method="ping",
            payload=json.dumps(
                {
                    "sequence": sequence,
                    "message": self.message_payload,
                    "timestamp": time.time(),
                }
            ),
        )

    def parse_pong_message(self, response_bytes: bytes) -> Dict[str, Any]:
        """
        Parse a pong response message.

        Attempts to decode and parse a JSON response from the server.
        If parsing fails, returns an error dictionary with the raw response.

        Args:
            response_bytes (bytes): Raw response from server

        Returns:
            Dict[str, Any]: Parsed pong message data or error information

        Raises:
            json.JSONDecodeError: If response is not valid JSON (caught and handled)
            UnicodeDecodeError: If response cannot be decoded as UTF-8 (caught
                and handled)
        """
        try:
            # For now, assume simple JSON response
            # In a full implementation, this would deserialize HydraMsg
            response_str = response_bytes.decode("utf-8")
            return json.loads(response_str)  # type: ignore
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.log.warning(f"Failed to parse pong response: {e}")
            return {
                "error": "Invalid response format",
                "raw": response_bytes.decode("utf-8", errors="replace"),
            }

    def send_ping(self, sequence: int) -> Optional[Dict[str, Any]]:
        """
        Send a single ping message and wait for pong response.

        Creates a ping message, sends it to the server, measures round-trip time,
        and parses the response. Updates internal counters for sent/received messages.

        Args:
            sequence (int): Sequence number for this ping

        Returns:
            Optional[Dict[str, Any]]: Parsed pong response or None if failed

        Raises:
            Exception: If message creation, sending, or parsing fails (caught
                and handled)
        """
        try:
            # Create structured ping message
            ping_msg = self.create_ping_message(sequence)

            # For now, serialize as JSON
            # (in full implementation, use HydraMsg serialization)
            ping_data = {
                "sender": ping_msg._sender,
                "target": ping_msg._target,
                "method": ping_msg._method,
                "payload": ping_msg._payload,
                "id": str(ping_msg._id),
            }

            ping_bytes = json.dumps(ping_data).encode("utf-8")

            self.log.info(f"Sending ping #{sequence} to {self.server_address}")
            self.sent_pings += 1

            # Send ping and wait for pong
            start_time = time.time()
            response_bytes = self.send_message(ping_bytes)
            end_time = time.time()

            # Parse pong response
            pong_data = self.parse_pong_message(response_bytes)

            if "error" not in pong_data:
                self.received_pongs += 1
                round_trip_time = (
                    end_time - start_time
                ) * 1000  # Convert to milliseconds
                self.log.info(f"Received pong #{sequence}: RTT={round_trip_time:.2f}ms")
                return pong_data
            else:
                self.log.error(f"Pong error for ping #{sequence}: {pong_data['error']}")
                return None

        except Exception as e:
            self.log.error(f"Failed to send ping #{sequence}: {e}")
            return None

    def run(self) -> None:
        """
        Run the ping client, sending the specified number of ping messages.

        Executes the main ping loop, sending messages at the configured interval
        and displaying a summary of results. Handles keyboard interruption gracefully
        and ensures proper cleanup of resources.

        Returns:
            None

        Raises:
            KeyboardInterrupt: When user interrupts with Ctrl+C (caught and handled)
        """
        self.log.info(
            f"Starting ping client: {self.ping_count} pings to {self.server_address}"
        )

        try:
            for i in range(1, self.ping_count + 1):
                self.send_ping(i)

                # Wait between pings (except for the last one)
                if i < self.ping_count and self.ping_interval > 0:
                    time.sleep(self.ping_interval)

            # Print summary
            success_rate = (
                (self.received_pongs / self.sent_pings) * 100
                if self.sent_pings > 0
                else 0
            )
            self.log.info(
                f"Ping summary: {self.received_pongs}/{self.sent_pings} "
                f"successful ({success_rate:.1f}%)"
            )

        except KeyboardInterrupt:
            self.log.info("Ping client interrupted by user")
        finally:
            self._cleanup()


def main() -> None:
    """
    Main entry point for hydra-ping-client command.

    Parses command line arguments, creates a HydraClientPing instance,
    and runs the ping client. Handles keyboard interruption and errors
    gracefully with appropriate exit codes.

    Returns:
        None

    Raises:
        KeyboardInterrupt: When user interrupts with Ctrl+C (handled)
        Exception: For any other errors during execution (handled)
    """
    parser = argparse.ArgumentParser(
        description="HydraRouter Ping Client - Send structured ping messages "
        "to a pong server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hydra-ping-client                                    # Send 1 ping to localhost:5757
  hydra-ping-client --hostname 192.168.1.100          # Ping remote server
  hydra-ping-client --port 8080                       # Ping different port
  hydra-ping-client --count 10 --interval 0.5         # Send 10 pings, 0.5s apart
  hydra-ping-client --message "Hello Server"          # Custom ping message
  hydra-ping-client --hostname server.com --port 9000 --count 5 --message "Test"
        """,
    )

    parser.add_argument(
        "--hostname",
        "-H",
        default=DHydraServerDef.HOSTNAME,
        help=f"Server hostname to connect to (default: {DHydraServerDef.HOSTNAME})",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DHydraServerDef.PORT,
        help=f"Server port to connect to (default: {DHydraServerDef.PORT})",
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of ping messages to send (default: 1)",
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=1.0,
        help="Interval between pings in seconds (default: 1.0)",
    )

    parser.add_argument(
        "--message",
        "-m",
        default="ping",
        help="Custom message payload for pings (default: 'ping')",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"hydra-ping-client {DHydra.VERSION}",
    )

    args = parser.parse_args()

    try:
        client = HydraClientPing(
            server_hostname=args.hostname,
            server_port=args.port,
            ping_count=args.count,
            ping_interval=args.interval,
            message_payload=args.message,
        )

        client.run()

    except KeyboardInterrupt:
        print("\nPing client stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Ping client error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
