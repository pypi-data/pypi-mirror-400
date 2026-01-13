import json
import os
import time
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


class StateLockError(RuntimeError):
    pass


class LocalState:
    FILE = Path(".cfddb.state.json")
    LOCK = Path(".cfddb.state.lock")

    def acquire_lock(self):
        if self.LOCK.exists():
            info = self.LOCK.read_text()
            raise StateLockError(
                f"State is locked.\n\nLock info:\n{info}\n\n"
                f"If this is stale, remove {self.LOCK} manually."
            )

        lock_info = {
            "pid": os.getpid(),
            "timestamp": time.time(),
        }
        self.LOCK.write_text(json.dumps(lock_info, indent=2))

    def release_lock(self):
        if self.LOCK.exists():
            self.LOCK.unlink()

    def load(self):
        if not self.FILE.exists():
            return {}
        return json.loads(self.FILE.read_text())

    def save_metadata(self, data: dict[str, Any]):
        self.FILE.write_text(json.dumps(data, indent=2))
