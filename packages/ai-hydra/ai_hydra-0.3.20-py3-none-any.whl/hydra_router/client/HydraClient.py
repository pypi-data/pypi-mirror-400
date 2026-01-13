#!/usr/bin/env python

import argparse
import sys
from typing import Optional

import zmq

from hydra_router.constants.DHydra import DHydraClientMsg, DHydraServerDef


class HydraClient:
    """
    HydraClient provides a simple ZeroMQ-based client that connects to a server
    and sends requests using the REQ/REP pattern.
    """

    def __init__(
        self, server_hostname: Optional[str] = None, server_port: Optional[int] = None
    ) -> None:
        """
        Initialize the HydraClient with server connection parameters.

        Args:
            server_address (str): The server address to connect to
                (default: "tcp://localhost:5555")
        """

        self._server_hostname = server_hostname or DHydraServerDef.HOSTNAME
        self._server_port = server_port or DHydraServerDef.PORT

        self.server_address = (
            "tcp://" + self._server_hostname + ":" + str(self._server_port)
        )
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self._setup_socket()

    def _setup_socket(self) -> None:
        """Set up ZeroMQ context and REQ socket with connection."""
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.server_address)
            print(DHydraClientMsg.CONNECTED.format(server_address=self.server_address))
        except Exception as e:
            print(DHydraClientMsg.ERROR.format(e=e))
            exit(1)

    def send_message(self, message: bytes) -> bytes:
        """
        Send a message to the server and wait for response.

        Args:
            message (bytes): The message to send to the server

        Returns:
            bytes: The response received from the server
        """
        try:
            print(DHydraClientMsg.SENDING.format(message=message))
            if self.socket is not None:
                self.socket.send(message)

                # Wait for response
                response: bytes = self.socket.recv()
                print(DHydraClientMsg.RECEIVED.format(response=response))
                return response
            else:
                raise RuntimeError("Socket not initialized")

        except Exception as e:
            print(DHydraClientMsg.ERROR.format(e=e))
            exit(1)

    def _cleanup(self) -> None:
        """Clean up ZeroMQ resources."""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        print(DHydraClientMsg.CLEANUP)


def main() -> None:
    """Main entry point for hydra-client command."""
    parser = argparse.ArgumentParser(
        description="Connect to a HydraServer and send messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hydra-client                          # Send "Hello" to localhost:5757
  hydra-client --hostname 192.168.1.100  # Connect to remote server
  hydra-client --port 8080              # Connect to different port
  hydra-client --message "Test message" # Send custom message
  hydra-client --count 5                # Send 5 messages
  hydra-client --hostname server.com --port 9000 --message "Custom" --count 3
        """,
    )

    parser.add_argument(
        "--hostname",
        "-H",
        default=DHydraServerDef.HOSTNAME,
        help=DHydraClientMsg.SERVER_HELP.format(
            server_address=DHydraServerDef.HOSTNAME
        ),
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DHydraServerDef.PORT,
        help=DHydraClientMsg.PORT_HELP.format(server_port=DHydraServerDef.PORT),
    )

    parser.add_argument(
        "--message",
        "-m",
        default="Hello",
        help="Message to send to server (default: 'Hello')",
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of messages to send (default: 1)",
    )

    parser.add_argument("--version", "-v", action="version", version="ai-hydra 0.1.0")

    args = parser.parse_args()

    try:
        print(f"Connecting to HydraServer at {args.hostname}:{args.port}")

        client = HydraClient(server_hostname=args.hostname, server_port=args.port)

        for i in range(args.count):
            if args.count > 1:
                print(f"\n--- Message {i + 1}/{args.count} ---")

            message = args.message.encode("utf-8")
            response = client.send_message(message)

            if args.count > 1:
                decoded_response = response.decode("utf-8", errors="replace")
                print(f"Response {i + 1}: {decoded_response}")

        client._cleanup()
        print("\nClient session completed successfully")

    except KeyboardInterrupt:
        print("\nClient stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Client error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
