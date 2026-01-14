"""
Public exception types for pyasyncspeedtest.
"""


class SpeedTestError(Exception):
    """Base exception for all speedtest errors."""
    pass


class ServerSelectionError(SpeedTestError):
    """Raised when server selection fails or no suitable server is found."""
    pass


class MeasurementError(SpeedTestError):
    """Raised when speed measurement prerequisites are not met."""
    pass


class ConfigurationError(SpeedTestError):
    """Raised when configuration fetching fails or is invalid."""
    pass
