"""File watcher utilities for SyncLangs."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class DebouncedEventHandler(FileSystemEventHandler):
    """Debounce file system events and invoke a callback."""

    def __init__(
        self,
        debounce_seconds: float,
        on_change: Callable[[Path], None],
    ) -> None:
        self._debounce_seconds = debounce_seconds
        self._on_change = on_change
        self._timer: threading.Timer | None = None
        self._last_path: Path | None = None
        self._lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix != ".syln":
            return
        with self._lock:
            self._last_path = path
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce_seconds, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def shutdown(self) -> None:
        """Cancel any pending debounce timer."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None

    def _fire(self) -> None:
        with self._lock:
            path = self._last_path
            self._timer = None
        if path is not None:
            self._on_change(path)


def start_watcher(
    input_dir: Path,
    debounce_ms: int,
    on_change: Callable[[Path], None],
    stop_event: threading.Event | None = None,
) -> None:
    """Start watching for .syln changes."""
    handler = DebouncedEventHandler(debounce_ms / 1000.0, on_change)
    observer = Observer()
    observer.schedule(handler, str(input_dir), recursive=True)
    observer.start()
    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        handler.shutdown()
        observer.stop()
        observer.join()
