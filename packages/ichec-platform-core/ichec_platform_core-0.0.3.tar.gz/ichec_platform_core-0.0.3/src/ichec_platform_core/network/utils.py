import time
import socket
import logging

logger = logging.getLogger(__name__)


def wait_for_ready(host: str, port: int, timeout: float = 5.0) -> bool:

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                logger.info("Server is ready")
                return True
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.1)

    logger.warning(f"Server not ready after {timeout}s timeout")
    return False
