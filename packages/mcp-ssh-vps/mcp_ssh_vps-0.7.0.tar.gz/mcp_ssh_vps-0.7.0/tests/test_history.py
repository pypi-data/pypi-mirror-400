"""Tests for command history."""

from datetime import datetime, timezone

import pytest

from sshmcp.tools.history import (
    CommandHistory,
    HistoryEntry,
    get_history,
    init_history,
)


class TestHistoryEntry:
    """Tests for HistoryEntry."""

    def test_create_entry(self):
        """Test creating a history entry."""
        entry = HistoryEntry(
            host="test-server",
            command="echo hello",
            exit_code=0,
            duration_ms=100,
        )

        assert entry.host == "test-server"
        assert entry.command == "echo hello"
        assert entry.exit_code == 0
        assert entry.duration_ms == 100

    def test_to_dict(self):
        """Test converting to dictionary."""
        entry = HistoryEntry(
            host="test-server",
            command="echo hello",
            exit_code=0,
        )

        data = entry.to_dict()

        assert data["host"] == "test-server"
        assert data["command"] == "echo hello"
        assert data["exit_code"] == 0
        assert "timestamp" in data

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "host": "test-server",
            "command": "uptime",
            "exit_code": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": 50,
        }

        entry = HistoryEntry.from_dict(data)

        assert entry.host == "test-server"
        assert entry.command == "uptime"
        assert entry.exit_code == 0

    def test_stdout_preview_truncation(self):
        """Test that stdout preview is truncated."""
        long_output = "x" * 500
        entry = HistoryEntry(
            host="test-server",
            command="echo",
            exit_code=0,
            stdout_preview=long_output,
        )

        data = entry.to_dict()
        assert len(data["stdout_preview"]) == 200


class TestCommandHistory:
    """Tests for CommandHistory."""

    def test_add_entry(self):
        """Test adding an entry."""
        history = CommandHistory()

        entry = history.add(
            host="server1",
            command="ls -la",
            exit_code=0,
            duration_ms=50,
        )

        assert entry.host == "server1"
        assert entry.command == "ls -la"

    def test_get_history(self):
        """Test getting history."""
        history = CommandHistory()

        history.add("server1", "cmd1", 0)
        history.add("server1", "cmd2", 0)
        history.add("server2", "cmd3", 1)

        # All history
        all_entries = history.get_history()
        assert len(all_entries) == 3

        # Filter by host
        server1_entries = history.get_history(host="server1")
        assert len(server1_entries) == 2

        # Success only
        success_entries = history.get_history(success_only=True)
        assert len(success_entries) == 2

        # Failed only
        failed_entries = history.get_history(failed_only=True)
        assert len(failed_entries) == 1

    def test_get_history_limit(self):
        """Test history limit."""
        history = CommandHistory()

        for i in range(10):
            history.add("server1", f"cmd{i}", 0)

        entries = history.get_history(limit=5)
        assert len(entries) == 5

    def test_search(self):
        """Test searching history."""
        history = CommandHistory()

        history.add("server1", "git pull", 0)
        history.add("server1", "git push", 0)
        history.add("server1", "npm install", 0)

        results = history.search("git")
        assert len(results) == 2

        results = history.search("npm")
        assert len(results) == 1

    def test_get_last_command(self):
        """Test getting last command."""
        history = CommandHistory()

        history.add("server1", "first", 0)
        history.add("server1", "second", 0)

        last = history.get_last_command("server1")
        assert last is not None
        assert last.command == "second"

        # Non-existent host
        last = history.get_last_command("nonexistent")
        assert last is None

    def test_get_hosts(self):
        """Test getting hosts with history."""
        history = CommandHistory()

        history.add("server1", "cmd", 0)
        history.add("server2", "cmd", 0)

        hosts = history.get_hosts()
        assert "server1" in hosts
        assert "server2" in hosts

    def test_get_stats(self):
        """Test getting statistics."""
        history = CommandHistory()

        history.add("server1", "cmd1", 0, duration_ms=100)
        history.add("server1", "cmd2", 1, duration_ms=200)
        history.add("server2", "cmd3", 0, duration_ms=300)

        stats = history.get_stats()
        assert stats["total_commands"] == 3
        assert stats["success_count"] == 2
        assert stats["failure_count"] == 1
        assert stats["success_rate"] == pytest.approx(66.7, rel=0.1)
        assert stats["hosts"] == 2

    def test_clear_host(self):
        """Test clearing history for specific host."""
        history = CommandHistory()

        history.add("server1", "cmd", 0)
        history.add("server2", "cmd", 0)

        cleared = history.clear("server1")
        assert cleared == 1

        hosts = history.get_hosts()
        assert "server1" not in hosts
        assert "server2" in hosts

    def test_clear_all(self):
        """Test clearing all history."""
        history = CommandHistory()

        history.add("server1", "cmd", 0)
        history.add("server2", "cmd", 0)

        cleared = history.clear()
        assert cleared == 2
        assert len(history.get_hosts()) == 0

    def test_max_entries_per_host(self):
        """Test max entries per host limit."""
        history = CommandHistory(max_entries_per_host=5)

        for i in range(10):
            history.add("server1", f"cmd{i}", 0)

        entries = history.get_history(host="server1")
        assert len(entries) == 5

    def test_max_total_entries(self):
        """Test max total entries limit."""
        history = CommandHistory(max_entries_per_host=10, max_total_entries=5)

        for i in range(10):
            history.add("server1", f"cmd{i}", 0)

        all_entries = history.get_history()
        assert len(all_entries) <= 5


class TestGlobalHistory:
    """Tests for global history functions."""

    def test_get_history_singleton(self):
        """Test getting global history."""
        h1 = get_history()
        h2 = get_history()
        assert isinstance(h1, CommandHistory)
        assert isinstance(h2, CommandHistory)

    def test_init_history(self):
        """Test initializing global history."""
        history = init_history(max_entries_per_host=50)
        assert history.max_entries_per_host == 50
