"""
pyasyncspeedtest - Async-first Python speed test library.

An async Python library for measuring network throughput via HTTP-based speed tests.
Designed to be embedded into async applications, services, and workers.
"""

from .runner import (
    AsyncSpeedtest,
    run_speedtest,
    SpeedTestResult,
    SpeedTestConfig,
    ServerInfo,
    SpeedTestError,
    ServerSelectionError,
    MeasurementError,
    ConfigurationError,
)

__version__ = "0.1.0"

__all__ = [
    "AsyncSpeedtest",
    "run_speedtest",
    "SpeedTestResult",
    "SpeedTestConfig",
    "ServerInfo",
    "SpeedTestError",
    "ServerSelectionError",
    "MeasurementError",
    "ConfigurationError",
]
