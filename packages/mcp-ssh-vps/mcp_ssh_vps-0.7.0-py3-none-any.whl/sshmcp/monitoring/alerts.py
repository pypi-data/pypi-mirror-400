"""System monitoring and alerting for VPS servers."""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

import structlog

from sshmcp.models.machine import MachineConfig
from sshmcp.ssh.client import SSHClient

logger = structlog.get_logger()


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to monitor."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    LOAD = "load"
    PROCESS = "process"


@dataclass
class AlertThreshold:
    """Threshold configuration for alerts."""

    metric: MetricType
    warning: float
    critical: float
    duration_seconds: int = 60  # How long threshold must be exceeded


@dataclass
class Alert:
    """Alert event."""

    host: str
    metric: MetricType
    severity: AlertSeverity
    value: float
    threshold: float
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "metric": self.metric.value,
            "severity": self.severity.value,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HostMetrics:
    """Current metrics for a host."""

    host: str
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    load_1min: float = 0.0
    load_5min: float = 0.0
    load_15min: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_percent": self.disk_percent,
            "load_1min": self.load_1min,
            "load_5min": self.load_5min,
            "load_15min": self.load_15min,
            "timestamp": self.timestamp.isoformat(),
        }


class AlertManager:
    """
    Monitors system metrics and generates alerts.
    """

    DEFAULT_THRESHOLDS = [
        AlertThreshold(MetricType.CPU, warning=80.0, critical=95.0),
        AlertThreshold(MetricType.MEMORY, warning=80.0, critical=95.0),
        AlertThreshold(MetricType.DISK, warning=80.0, critical=95.0),
        AlertThreshold(MetricType.LOAD, warning=2.0, critical=5.0),
    ]

    def __init__(
        self,
        check_interval: int = 60,
        thresholds: list[AlertThreshold] | None = None,
    ) -> None:
        """
        Initialize alert manager.

        Args:
            check_interval: Seconds between metric checks.
            thresholds: Custom alert thresholds.
        """
        self.check_interval = check_interval
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()

        self._machines: dict[str, MachineConfig] = {}
        self._metrics: dict[str, HostMetrics] = {}
        self._alerts: list[Alert] = []
        self._active_alerts: dict[str, Alert] = {}  # host:metric -> alert
        self._callbacks: list[Callable[[Alert], None]] = []

        self._lock = threading.Lock()
        self._shutdown = threading.Event()
        self._monitor_thread: threading.Thread | None = None

    def register_machine(self, machine: MachineConfig) -> None:
        """Register a machine for monitoring."""
        with self._lock:
            self._machines[machine.name] = machine
        logger.info("alert_machine_registered", host=machine.name)

    def unregister_machine(self, name: str) -> None:
        """Unregister a machine from monitoring."""
        with self._lock:
            if name in self._machines:
                del self._machines[name]
            if name in self._metrics:
                del self._metrics[name]
        logger.info("alert_machine_unregistered", host=name)

    def set_threshold(
        self,
        metric: MetricType,
        warning: float,
        critical: float,
        duration: int = 60,
    ) -> None:
        """
        Set or update a threshold.

        Args:
            metric: Metric type.
            warning: Warning threshold.
            critical: Critical threshold.
            duration: Duration in seconds.
        """
        # Remove existing threshold for this metric
        self.thresholds = [t for t in self.thresholds if t.metric != metric]
        self.thresholds.append(AlertThreshold(metric, warning, critical, duration))

    def register_callback(self, callback: Callable[[Alert], None]) -> None:
        """Register a callback for alert events."""
        self._callbacks.append(callback)

    def start_monitoring(self) -> None:
        """Start background monitoring."""
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return

        self._shutdown.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="alert-monitor",
        )
        self._monitor_thread.start()
        logger.info("alert_monitoring_started")

    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self._shutdown.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
        logger.info("alert_monitoring_stopped")

    def check_host(self, name: str) -> HostMetrics | None:
        """
        Check metrics for a single host.

        Args:
            name: Host name.

        Returns:
            HostMetrics or None if check failed.
        """
        with self._lock:
            if name not in self._machines:
                return None
            machine = self._machines[name]

        try:
            client = SSHClient(machine)
            client.connect(retry=False)

            try:
                metrics = self._collect_metrics(client, name)

                with self._lock:
                    self._metrics[name] = metrics

                self._check_thresholds(metrics)
                return metrics

            finally:
                client.disconnect()

        except Exception as e:
            logger.error("alert_check_failed", host=name, error=str(e))
            return None

    def get_metrics(self, name: str | None = None) -> dict[str, HostMetrics]:
        """
        Get current metrics.

        Args:
            name: Optional host name filter.

        Returns:
            Dictionary of host metrics.
        """
        with self._lock:
            if name:
                if name in self._metrics:
                    return {name: self._metrics[name]}
                return {}
            return dict(self._metrics)

    def get_alerts(
        self,
        host: str | None = None,
        severity: AlertSeverity | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """
        Get alert history.

        Args:
            host: Filter by host.
            severity: Filter by severity.
            limit: Maximum alerts to return.

        Returns:
            List of alerts.
        """
        with self._lock:
            alerts = list(self._alerts)

        if host:
            alerts = [a for a in alerts if a.host == host]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        # Sort by timestamp descending
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]

    def get_active_alerts(self) -> list[Alert]:
        """Get currently active alerts."""
        with self._lock:
            return list(self._active_alerts.values())

    def clear_alert(self, host: str, metric: MetricType) -> bool:
        """
        Clear an active alert.

        Args:
            host: Host name.
            metric: Metric type.

        Returns:
            True if alert was cleared.
        """
        key = f"{host}:{metric.value}"
        with self._lock:
            if key in self._active_alerts:
                del self._active_alerts[key]
                return True
        return False

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while not self._shutdown.is_set():
            with self._lock:
                machines = list(self._machines.values())

            for machine in machines:
                if self._shutdown.is_set():
                    break
                self.check_host(machine.name)

            self._shutdown.wait(timeout=self.check_interval)

    def _collect_metrics(self, client: SSHClient, host: str) -> HostMetrics:
        """Collect metrics from a host."""
        metrics = HostMetrics(host=host)

        # Get CPU usage
        try:
            result = client.execute("top -bn1 | grep 'Cpu' | awk '{print 100-$8}'")
            if result.exit_code == 0 and result.stdout.strip():
                metrics.cpu_percent = float(result.stdout.strip())
        except Exception:
            pass

        # Get memory usage
        try:
            result = client.execute("free | grep Mem | awk '{print $3/$2 * 100}'")
            if result.exit_code == 0 and result.stdout.strip():
                metrics.memory_percent = float(result.stdout.strip())
        except Exception:
            pass

        # Get disk usage
        try:
            result = client.execute("df / | tail -1 | awk '{print $5}' | tr -d '%'")
            if result.exit_code == 0 and result.stdout.strip():
                metrics.disk_percent = float(result.stdout.strip())
        except Exception:
            pass

        # Get load average
        try:
            result = client.execute("cat /proc/loadavg")
            if result.exit_code == 0:
                parts = result.stdout.split()
                if len(parts) >= 3:
                    metrics.load_1min = float(parts[0])
                    metrics.load_5min = float(parts[1])
                    metrics.load_15min = float(parts[2])
        except Exception:
            pass

        return metrics

    def _check_thresholds(self, metrics: HostMetrics) -> None:
        """Check metrics against thresholds and generate alerts."""
        for threshold in self.thresholds:
            value = self._get_metric_value(metrics, threshold.metric)
            if value is None:
                continue

            severity = None
            if value >= threshold.critical:
                severity = AlertSeverity.CRITICAL
            elif value >= threshold.warning:
                severity = AlertSeverity.WARNING

            key = f"{metrics.host}:{threshold.metric.value}"

            if severity:
                alert = Alert(
                    host=metrics.host,
                    metric=threshold.metric,
                    severity=severity,
                    value=value,
                    threshold=threshold.critical
                    if severity == AlertSeverity.CRITICAL
                    else threshold.warning,
                    message=f"{threshold.metric.value} is {value:.1f}% (threshold: {threshold.warning}/{threshold.critical})",
                )

                with self._lock:
                    # Only notify if new or severity changed
                    existing = self._active_alerts.get(key)
                    if not existing or existing.severity != severity:
                        self._active_alerts[key] = alert
                        self._alerts.append(alert)

                        # Limit alert history
                        if len(self._alerts) > 1000:
                            self._alerts = self._alerts[-500:]

                # Notify callbacks
                if not existing or existing.severity != severity:
                    for callback in self._callbacks:
                        try:
                            callback(alert)
                        except Exception:
                            pass

                    logger.warning(
                        "alert_triggered",
                        host=metrics.host,
                        metric=threshold.metric.value,
                        severity=severity.value,
                        value=value,
                    )
            else:
                # Clear alert if below threshold
                with self._lock:
                    if key in self._active_alerts:
                        del self._active_alerts[key]
                        logger.info(
                            "alert_cleared",
                            host=metrics.host,
                            metric=threshold.metric.value,
                        )

    def _get_metric_value(
        self, metrics: HostMetrics, metric_type: MetricType
    ) -> float | None:
        """Get metric value by type."""
        if metric_type == MetricType.CPU:
            return metrics.cpu_percent
        elif metric_type == MetricType.MEMORY:
            return metrics.memory_percent
        elif metric_type == MetricType.DISK:
            return metrics.disk_percent
        elif metric_type == MetricType.LOAD:
            return metrics.load_1min
        return None


# Global alert manager instance
_alert_manager: AlertManager | None = None


def get_alert_manager() -> AlertManager:
    """Get or create the global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def init_alert_manager(
    check_interval: int = 60,
    thresholds: list[AlertThreshold] | None = None,
) -> AlertManager:
    """
    Initialize the global alert manager.

    Args:
        check_interval: Seconds between checks.
        thresholds: Custom thresholds.

    Returns:
        Initialized AlertManager.
    """
    global _alert_manager
    _alert_manager = AlertManager(
        check_interval=check_interval,
        thresholds=thresholds,
    )
    return _alert_manager
