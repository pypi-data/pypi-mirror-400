import logging
import re
import time

logger = logging.getLogger(__name__)

class _WebSocketLogFilter(logging.Filter):
    """
    Prettifies raw websockets library logs for better CDP debugging.
    
    Transforms verbose websocket protocol messages into concise, 
    readable format with latency tracking for PING/PONG.
    """

    def __init__(self) -> None:
        super().__init__()
        self._ping_times: dict[str, float] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name != "websockets.client":
            return True

        record.name = "cdpify.ws"
        msg = record.getMessage()

        if result := self._handle_ping_pong(msg, record):
            return result
        
        if self._should_suppress(msg):
            return False
        
        if self._handle_connection_state(msg, record):
            return True

        return True

    def _handle_ping_pong(self, msg: str, record: logging.LogRecord) -> bool | None:
        if "> PING" in msg:
            if match := re.search(r"> PING ([a-f0-9 ]+)", msg):
                self._ping_times[match.group(1)] = time.time()
            return False

        if "< PONG" in msg:
            if match := re.search(r"< PONG ([a-f0-9 ]+)", msg):
                ping_data = match.group(1)
                if start_time := self._ping_times.pop(ping_data, None):
                    latency_ms = (time.time() - start_time) * 1000
                    record.msg = f"✔ PING ({latency_ms:.1f}ms)"
                    record.args = ()
                    return True
            return False

        return None

    def _should_suppress(self, msg: str) -> bool:
        noise_patterns = ("keepalive", "> EOF", "< EOF", "% sent", "% received")
        return any(pattern in msg for pattern in noise_patterns)

    def _handle_connection_state(self, msg: str, record: logging.LogRecord) -> bool:
        if "= connection is" not in msg:
            return False

        state_map = {
            "CONNECTING": "🔗 Connecting...",
            "OPEN": "✅ WebSocket connected",
            "CLOSING": "🔌 Disconnecting...",
            "CLOSED": "🔌 Disconnected",
        }

        for state, formatted in state_map.items():
            if state in msg:
                record.msg = formatted
                record.args = ()
                return True

        return False


def configure_websocket_logging() -> None:
    """
    Enable prettified websocket logging for CDP debugging.
    
    Call once at application startup to transform verbose websocket
    protocol logs into readable CDP-focused output.
    
    Example:
        import logging
        from cdpify.client import configure_websocket_logging
        
        logging.basicConfig(level=logging.DEBUG)
        configure_websocket_logging()
    """
    ws_logger = logging.getLogger("websockets.client")
    
    if not any(isinstance(f, _WebSocketLogFilter) for f in ws_logger.filters):
        ws_logger.addFilter(_WebSocketLogFilter())

