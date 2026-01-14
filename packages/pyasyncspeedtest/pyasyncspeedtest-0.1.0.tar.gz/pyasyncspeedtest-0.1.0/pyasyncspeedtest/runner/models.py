"""
Public data models for pyasyncspeedtest.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerInfo:
    """Information about a speedtest server."""
    url: str
    lat: float
    lon: float
    name: str
    country: str
    id: str
    distance: Optional[float] = None
    latency: Optional[float] = None


@dataclass
class SpeedTestConfig:
    """Configuration for speedtest execution."""
    source_address: Optional[str] = None
    download_test_duration: int = 15
    upload_test_duration: int = 10
    max_server_distance: int = 500
    debug: bool = False


@dataclass
class SpeedTestResult:
    """Results from a completed speedtest."""
    download: float  # bytes per second
    upload: float  # bytes per second
    ping: float  # milliseconds
    server: Optional[ServerInfo] = None
    public_ip: str = ""
    isp: str = ""

    @property
    def download_mbps(self) -> float:
        """Download speed in Mbps."""
        return self.download * 8 / 1_000_000

    @property
    def upload_mbps(self) -> float:
        """Upload speed in Mbps."""
        return self.upload * 8 / 1_000_000
