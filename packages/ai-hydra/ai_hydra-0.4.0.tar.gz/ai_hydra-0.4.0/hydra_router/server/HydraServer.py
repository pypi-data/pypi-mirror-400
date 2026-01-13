#!/usr/bin/env python

import argparse
import sys
from typing import Optional

import zmq

from hydra_router.constants.DHydra import DHydra, DHydraServerDef, DHydraServerMsg


class HydraServer:
    """
    HydraServer provides a simple ZeroMQ-based server that binds to a port
    and handles client requests using the REQ/REP pattern.
    """

    def __init__(self, address: str = "*", port: int = DHydraServerDef.PORT):
        """
        Initialize the HydraServer with binding parameters.

        Args:
            address (str): The address to bind to (default: "*" for all
                interfaces)
            port (int): The port to bind to (default: 5555)
        """
        self.address = address
        self.port = port
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None

    def _setup_socket(self) -> None:
        """Set up ZeroMQ context and REP socket."""
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        bind_address = f"tcp://{self.address}:{self.port}"
        self.socket.bind(bind_address)
        print(DHydraServerMsg.BIND.format(bind_address=bind_address))

    def start(self) -> None:
        """
        Start the server and begin listening for requests in a continuous loop.
        This method will run indefinitely until interrupted.
        """
        if self.socket is None:
            self._setup_socket()
        print(DHydraServerMsg.LOOP_UP.format(address=self.address, port=self.port))

        try:
            while True:
                # Wait for next request from client
                if self.socket is not None:
                    message = self.socket.recv()
                    print(DHydraServerMsg.RECEIVE.format(message=message))

                    # Send reply back to client (simple echo for now)
                    response = b"World"
                    self.socket.send(response)
                    print(DHydraServerMsg.SENT.format(response=response))
                else:
                    raise RuntimeError("Socket not initialized")

        except KeyboardInterrupt:
            print(DHydraServerMsg.SHUTDOWN)
        except Exception as e:
            print(DHydraServerMsg.ERROR.format(e=e))
            exit(1)
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up ZeroMQ resources."""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        print(DHydraServerMsg.CLEANUP)


def main() -> None:
    """Main entry point for hydra-server command."""
    parser = argparse.ArgumentParser(
        description="Start a HydraServer instance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hydra-server                          # Start server on default (*:5757)
  hydra-server --port 8080              # Start server on port 8080
  hydra-server --address localhost      # Start server on localhost:5757
  hydra-server --address 0.0.0.0 --port 9000  # Start on all interfaces
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
        "--version", "-v", action="version", version="ai-hydra " + DHydra.VERSION
    )

    args = parser.parse_args()

    try:
        print(DHydraServerMsg.STARTING.format(address=args.address, port=args.port))
        print(DHydraServerMsg.STOP_HELP)

        server = HydraServer(address=args.address, port=args.port)
        server.start()

    except KeyboardInterrupt:
        print(DHydraServerMsg.USER_STOP)
        sys.exit(0)
    except Exception as e:
        print(DHydraServerMsg.ERROR.format(e=e))
        sys.exit(1)


if __name__ == "__main__":
    main()
