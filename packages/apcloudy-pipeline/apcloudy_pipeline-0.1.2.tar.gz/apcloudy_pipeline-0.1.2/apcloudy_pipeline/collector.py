"""
Unified data collector for bundling requests, items, and logs together.
"""
from threading import Lock


class DataCollector:
    """
    Collects all data (requests, items, logs) in batches and sends them together.
    Thread-safe singleton per crawler.
    """

    def __init__(self):
        self.requests = []
        self.items = []
        self.logs = []
        self.stats = None
        self.lock = Lock()

    def add_request(self, request_log: dict):
        """Add a request log to the batch"""
        with self.lock:
            self.requests.append(request_log)

    def add_item(self, item: dict):
        """Add an item to the batch"""
        with self.lock:
            self.items.append(item)

    def add_log(self, log_entry: dict):
        """Add a log entry to the batch"""
        with self.lock:
            self.logs.append(log_entry)

    def set_stats(self, stats: dict):
        """Set stats data (replaces existing stats)"""
        with self.lock:
            self.stats = stats

    def get_and_clear(self) -> dict | None:
        """Get all collected data and clear the buffers. Returns None if no data."""
        with self.lock:
            # Return None if there's no data to send
            if not (self.requests or self.items or self.logs or self.stats):
                return None

            data = {
                "requests": self.requests[:],
                "items": self.items[:],
                "logs": self.logs[:]
            }

            # Add stats if available
            if self.stats:
                data["stats"] = self.stats

            self.requests.clear()
            self.items.clear()
            self.logs.clear()
            self.stats = None
            return data

    def has_data(self) -> bool:
        """Check if there's any data to send"""
        with self.lock:
            return bool(self.requests or self.items or self.logs or self.stats)

    def size(self) -> int:
        """Get total number of collected items"""
        with self.lock:
            return len(self.requests) + len(self.items) + len(self.logs)
