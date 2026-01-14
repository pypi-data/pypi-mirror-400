"""Command history tracking for SSH MCP."""

import json
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class HistoryEntry:
    """Single command history entry."""

    host: str
    command: str
    exit_code: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    stdout_preview: str = ""
    stderr_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "command": self.command,
            "exit_code": self.exit_code,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "stdout_preview": self.stdout_preview[:200] if self.stdout_preview else "",
            "stderr_preview": self.stderr_preview[:200] if self.stderr_preview else "",
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryEntry":
        """Create from dictionary."""
        return cls(
            host=data["host"],
            command=data["command"],
            exit_code=data["exit_code"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            duration_ms=data.get("duration_ms", 0),
            stdout_preview=data.get("stdout_preview", ""),
            stderr_preview=data.get("stderr_preview", ""),
        )


class CommandHistory:
    """
    Command history manager.

    Tracks executed commands per host with optional persistence.
    """

    def __init__(
        self,
        max_entries_per_host: int = 100,
        max_total_entries: int = 1000,
        persistence_file: str | None = None,
    ) -> None:
        """
        Initialize command history.

        Args:
            max_entries_per_host: Maximum entries to keep per host.
            max_total_entries: Maximum total entries across all hosts.
            persistence_file: Optional file to persist history.
        """
        self.max_entries_per_host = max_entries_per_host
        self.max_total_entries = max_total_entries
        self.persistence_file = persistence_file

        self._history: dict[str, deque[HistoryEntry]] = {}
        self._lock = threading.Lock()
        self._total_count = 0

        if persistence_file:
            self._load()

    def add(
        self,
        host: str,
        command: str,
        exit_code: int,
        duration_ms: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> HistoryEntry:
        """
        Add a command to history.

        Args:
            host: Host where command was executed.
            command: The command that was executed.
            exit_code: Command exit code.
            duration_ms: Execution duration in milliseconds.
            stdout: Standard output (will be truncated).
            stderr: Standard error (will be truncated).

        Returns:
            The created history entry.
        """
        entry = HistoryEntry(
            host=host,
            command=command,
            exit_code=exit_code,
            duration_ms=duration_ms,
            stdout_preview=stdout[:200] if stdout else "",
            stderr_preview=stderr[:200] if stderr else "",
        )

        with self._lock:
            if host not in self._history:
                self._history[host] = deque(maxlen=self.max_entries_per_host)

            self._history[host].append(entry)
            self._total_count += 1

            # Enforce total limit
            while self._total_count > self.max_total_entries:
                self._evict_oldest()

        if self.persistence_file:
            self._save()

        return entry

    def get_history(
        self,
        host: str | None = None,
        limit: int = 50,
        success_only: bool = False,
        failed_only: bool = False,
    ) -> list[HistoryEntry]:
        """
        Get command history.

        Args:
            host: Filter by host (None for all hosts).
            limit: Maximum entries to return.
            success_only: Only return successful commands.
            failed_only: Only return failed commands.

        Returns:
            List of history entries, newest first.
        """
        with self._lock:
            if host:
                entries = list(self._history.get(host, []))
            else:
                entries = []
                for host_entries in self._history.values():
                    entries.extend(host_entries)

        # Filter
        if success_only:
            entries = [e for e in entries if e.exit_code == 0]
        elif failed_only:
            entries = [e for e in entries if e.exit_code != 0]

        # Sort by timestamp descending and limit
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def search(
        self,
        pattern: str,
        host: str | None = None,
        limit: int = 50,
    ) -> list[HistoryEntry]:
        """
        Search command history.

        Args:
            pattern: Pattern to search for in commands.
            host: Filter by host.
            limit: Maximum entries to return.

        Returns:
            Matching history entries.
        """
        entries = self.get_history(host=host, limit=self.max_total_entries)
        pattern_lower = pattern.lower()
        matches = [e for e in entries if pattern_lower in e.command.lower()]
        return matches[:limit]

    def get_last_command(self, host: str) -> HistoryEntry | None:
        """
        Get the last command executed on a host.

        Args:
            host: Host name.

        Returns:
            Last history entry or None.
        """
        with self._lock:
            if host in self._history and self._history[host]:
                return self._history[host][-1]
        return None

    def get_hosts(self) -> list[str]:
        """Get list of hosts with history."""
        with self._lock:
            return list(self._history.keys())

    def get_stats(self, host: str | None = None) -> dict[str, Any]:
        """
        Get history statistics.

        Args:
            host: Filter by host (None for all).

        Returns:
            Statistics dictionary.
        """
        entries = self.get_history(host=host, limit=self.max_total_entries)

        if not entries:
            return {
                "total_commands": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
            }

        success_count = sum(1 for e in entries if e.exit_code == 0)
        failure_count = len(entries) - success_count

        return {
            "total_commands": len(entries),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": round(success_count / len(entries) * 100, 1),
            "avg_duration_ms": round(
                sum(e.duration_ms for e in entries) / len(entries)
            ),
            "hosts": len(set(e.host for e in entries)),
        }

    def clear(self, host: str | None = None) -> int:
        """
        Clear history.

        Args:
            host: Host to clear (None for all).

        Returns:
            Number of entries cleared.
        """
        with self._lock:
            if host:
                if host in self._history:
                    count = len(self._history[host])
                    del self._history[host]
                    self._total_count -= count
                    return count
                return 0
            else:
                count = self._total_count
                self._history.clear()
                self._total_count = 0
                return count

    def _evict_oldest(self) -> None:
        """Evict oldest entry across all hosts."""
        oldest_host = None
        oldest_time = None

        for host, entries in self._history.items():
            if entries:
                entry_time = entries[0].timestamp
                if oldest_time is None or entry_time < oldest_time:
                    oldest_time = entry_time
                    oldest_host = host

        if oldest_host and self._history[oldest_host]:
            self._history[oldest_host].popleft()
            self._total_count -= 1

            if not self._history[oldest_host]:
                del self._history[oldest_host]

    def _save(self) -> None:
        """Save history to file."""
        if not self.persistence_file:
            return

        try:
            path = Path(self.persistence_file)
            path.parent.mkdir(parents=True, exist_ok=True)

            with self._lock:
                data = {
                    host: [e.to_dict() for e in entries]
                    for host, entries in self._history.items()
                }

            with open(path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error("history_save_error", error=str(e))

    def _load(self) -> None:
        """Load history from file."""
        if not self.persistence_file:
            return

        path = Path(self.persistence_file)
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            with self._lock:
                for host, entries in data.items():
                    self._history[host] = deque(
                        [HistoryEntry.from_dict(e) for e in entries],
                        maxlen=self.max_entries_per_host,
                    )
                    self._total_count += len(self._history[host])

            logger.info("history_loaded", entries=self._total_count)

        except Exception as e:
            logger.error("history_load_error", error=str(e))


# Global history instance
_history: CommandHistory | None = None


def get_history() -> CommandHistory:
    """Get or create the global command history."""
    global _history
    if _history is None:
        _history = CommandHistory()
    return _history


def init_history(
    max_entries_per_host: int = 100,
    max_total_entries: int = 1000,
    persistence_file: str | None = None,
) -> CommandHistory:
    """
    Initialize the global command history.

    Args:
        max_entries_per_host: Maximum entries per host.
        max_total_entries: Maximum total entries.
        persistence_file: Optional persistence file path.

    Returns:
        Initialized CommandHistory.
    """
    global _history
    _history = CommandHistory(
        max_entries_per_host=max_entries_per_host,
        max_total_entries=max_total_entries,
        persistence_file=persistence_file,
    )
    return _history
