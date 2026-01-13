# Project globals
class DHydra:
    """Project Defaults"""

    VERSION: str = "0.9.1"


# HydraServer defaults
class DHydraServerDef:
    """Hydra Server Defaults"""

    HOSTNAME: str = "localhost"
    PORT: int = 5757


# HydraClient messages
class DHydraClientMsg:
    """Hydra Client"""

    CLEANUP: str = "HydraClient cleanup complete"
    CONNECTED: str = "HydraClient connected to {server_address}"
    ERROR: str = "HydraClient error: {e}"
    PORT_HELP: str = "Server port to connect to (default: {server_port})"
    RECEIVED: str = "Received response: {response}"
    SENDING: str = "Sending request: {message}"
    SERVER_HELP: str = "Server hostname to connect to (default: {server})"


# HydraServer messages
class DHydraServerMsg:
    """Hydra Server Messages"""

    ADDRESS_HELP: str = "Address to bind to (default: '*' for all interfaces)"
    BIND: str = "HydraServer bound to {bind_address}"
    CLEANUP: str = "HydraServer cleanup complete"
    ERROR: str = "HydraServer error: {e}"
    LOOP_UP: str = "HydraServer message loop on {address}:{port} is up and running"
    PORT_HELP: str = "Port to bind to (default: {port})"
    RECEIVE: str = "Received request: {message}"
    SENT: str = "Sent response: {response}"
    SHUTDOWN: str = "HydraServer shutting down..."
    STARTING: str = "Starting HydraServer on {address}:{port}"
    STOP_HELP: str = "Press Ctrl+C to stop the server"
    USER_STOP: str = "Server stopped by user"
