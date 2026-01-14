"""Tests for monitoring and alerts."""

from unittest.mock import MagicMock

import pytest

from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig
from sshmcp.monitoring.alerts import (
    Alert,
    AlertManager,
    AlertSeverity,
    AlertThreshold,
    HostMetrics,
    MetricType,
    get_alert_manager,
    init_alert_manager,
)


@pytest.fixture
def mock_machine():
    """Create a mock machine configuration."""
    return MachineConfig(
        name="test-server",
        host="192.168.1.1",
        port=22,
        user="testuser",
        auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
        security=SecurityConfig(),
    )


class TestAlert:
    """Tests for Alert dataclass."""

    def test_create_alert(self):
        """Test creating an alert."""
        alert = Alert(
            host="test-server",
            metric=MetricType.CPU,
            severity=AlertSeverity.WARNING,
            value=85.0,
            threshold=80.0,
            message="CPU high",
        )

        assert alert.host == "test-server"
        assert alert.metric == MetricType.CPU
        assert alert.severity == AlertSeverity.WARNING

    def test_alert_to_dict(self):
        """Test alert to_dict method."""
        alert = Alert(
            host="test-server",
            metric=MetricType.MEMORY,
            severity=AlertSeverity.CRITICAL,
            value=96.0,
            threshold=95.0,
            message="Memory critical",
        )

        data = alert.to_dict()

        assert data["host"] == "test-server"
        assert data["metric"] == "memory"
        assert data["severity"] == "critical"
        assert data["value"] == 96.0
        assert "timestamp" in data


class TestHostMetrics:
    """Tests for HostMetrics dataclass."""

    def test_create_metrics(self):
        """Test creating host metrics."""
        metrics = HostMetrics(
            host="test-server",
            cpu_percent=50.0,
            memory_percent=60.0,
            disk_percent=70.0,
        )

        assert metrics.host == "test-server"
        assert metrics.cpu_percent == 50.0

    def test_metrics_to_dict(self):
        """Test metrics to_dict method."""
        metrics = HostMetrics(
            host="test-server",
            cpu_percent=50.0,
            memory_percent=60.0,
            load_1min=1.5,
        )

        data = metrics.to_dict()

        assert data["host"] == "test-server"
        assert data["cpu_percent"] == 50.0
        assert data["load_1min"] == 1.5


class TestAlertThreshold:
    """Tests for AlertThreshold."""

    def test_create_threshold(self):
        """Test creating a threshold."""
        threshold = AlertThreshold(
            metric=MetricType.CPU,
            warning=80.0,
            critical=95.0,
        )

        assert threshold.metric == MetricType.CPU
        assert threshold.warning == 80.0
        assert threshold.critical == 95.0
        assert threshold.duration_seconds == 60


class TestAlertManager:
    """Tests for AlertManager."""

    def test_init_default_thresholds(self):
        """Test manager has default thresholds."""
        manager = AlertManager()

        assert len(manager.thresholds) > 0
        metrics = [t.metric for t in manager.thresholds]
        assert MetricType.CPU in metrics
        assert MetricType.MEMORY in metrics

    def test_register_machine(self, mock_machine):
        """Test registering a machine."""
        manager = AlertManager()
        manager.register_machine(mock_machine)

        assert "test-server" in manager._machines

    def test_unregister_machine(self, mock_machine):
        """Test unregistering a machine."""
        manager = AlertManager()
        manager.register_machine(mock_machine)
        manager.unregister_machine("test-server")

        assert "test-server" not in manager._machines

    def test_set_threshold(self):
        """Test setting custom threshold."""
        manager = AlertManager()
        manager.set_threshold(MetricType.CPU, warning=70.0, critical=90.0)

        cpu_thresholds = [t for t in manager.thresholds if t.metric == MetricType.CPU]
        assert len(cpu_thresholds) == 1
        assert cpu_thresholds[0].warning == 70.0
        assert cpu_thresholds[0].critical == 90.0

    def test_register_callback(self):
        """Test registering alert callback."""
        manager = AlertManager()
        callback = MagicMock()
        manager.register_callback(callback)

        assert callback in manager._callbacks

    def test_get_metrics_empty(self):
        """Test getting metrics when none collected."""
        manager = AlertManager()
        metrics = manager.get_metrics()

        assert metrics == {}

    def test_get_alerts_empty(self):
        """Test getting alerts when none triggered."""
        manager = AlertManager()
        alerts = manager.get_alerts()

        assert alerts == []

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = AlertManager()

        # Manually add an active alert
        alert = Alert(
            host="test",
            metric=MetricType.CPU,
            severity=AlertSeverity.WARNING,
            value=85.0,
            threshold=80.0,
            message="test",
        )
        manager._active_alerts["test:cpu"] = alert

        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].host == "test"

    def test_clear_alert(self):
        """Test clearing an alert."""
        manager = AlertManager()

        alert = Alert(
            host="test",
            metric=MetricType.CPU,
            severity=AlertSeverity.WARNING,
            value=85.0,
            threshold=80.0,
            message="test",
        )
        manager._active_alerts["test:cpu"] = alert

        result = manager.clear_alert("test", MetricType.CPU)
        assert result is True
        assert len(manager.get_active_alerts()) == 0

    def test_clear_alert_not_exists(self):
        """Test clearing non-existent alert."""
        manager = AlertManager()
        result = manager.clear_alert("test", MetricType.CPU)
        assert result is False

    def test_check_thresholds_triggers_warning(self):
        """Test that warning threshold triggers alert."""
        manager = AlertManager()
        manager.set_threshold(MetricType.CPU, warning=80.0, critical=95.0)

        metrics = HostMetrics(host="test", cpu_percent=85.0)
        manager._check_thresholds(metrics)

        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].severity == AlertSeverity.WARNING

    def test_check_thresholds_triggers_critical(self):
        """Test that critical threshold triggers alert."""
        manager = AlertManager()
        manager.set_threshold(MetricType.CPU, warning=80.0, critical=95.0)

        metrics = HostMetrics(host="test", cpu_percent=97.0)
        manager._check_thresholds(metrics)

        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].severity == AlertSeverity.CRITICAL

    def test_check_thresholds_clears_alert(self):
        """Test that falling below threshold clears alert."""
        manager = AlertManager()
        manager.set_threshold(MetricType.CPU, warning=80.0, critical=95.0)

        # First trigger alert
        metrics = HostMetrics(host="test", cpu_percent=85.0)
        manager._check_thresholds(metrics)
        assert len(manager.get_active_alerts()) == 1

        # Then clear it
        metrics = HostMetrics(host="test", cpu_percent=50.0)
        manager._check_thresholds(metrics)
        assert len(manager.get_active_alerts()) == 0

    def test_callback_called_on_alert(self):
        """Test that callback is called when alert triggered."""
        manager = AlertManager()
        manager.set_threshold(MetricType.CPU, warning=80.0, critical=95.0)

        callback = MagicMock()
        manager.register_callback(callback)

        metrics = HostMetrics(host="test", cpu_percent=85.0)
        manager._check_thresholds(metrics)

        callback.assert_called_once()
        alert = callback.call_args[0][0]
        assert alert.host == "test"
        assert alert.severity == AlertSeverity.WARNING


class TestGlobalAlertManager:
    """Tests for global alert manager functions."""

    def test_get_alert_manager(self):
        """Test getting global manager."""
        manager = get_alert_manager()
        assert isinstance(manager, AlertManager)

    def test_init_alert_manager(self):
        """Test initializing global manager."""
        manager = init_alert_manager(check_interval=30)
        assert manager.check_interval == 30
