import os
import threading
import time


BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CUSTOM_EPOCH_MS = 1704067200000


class SnowflakeGenerator:
    def __init__(self, worker_id: int) -> None:
        self.worker_id = worker_id & 0x3FF
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def generate(self) -> int:
        with self.lock:
            timestamp = self._current_timestamp()
            if timestamp < self.last_timestamp:
                timestamp = self.last_timestamp

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp
            return ((timestamp - CUSTOM_EPOCH_MS) << 22) | (self.worker_id << 12) | self.sequence

    @staticmethod
    def _current_timestamp() -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, current_timestamp: int) -> int:
        timestamp = self._current_timestamp()
        while timestamp <= current_timestamp:
            timestamp = self._current_timestamp()
        return timestamp


def encode_base62(number: int) -> str:
    if number == 0:
        return BASE62_ALPHABET[0]

    encoded: list[str] = []
    while number > 0:
        number, remainder = divmod(number, 62)
        encoded.append(BASE62_ALPHABET[remainder])
    return "".join(reversed(encoded))


def resolve_node_id() -> str:
    return os.getenv("NODE_ID", os.getenv("HOSTNAME", "node-local"))

