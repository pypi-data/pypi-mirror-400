"""Custom exceptions for DanceIR toolbox."""


class DanceIRError(Exception):
    """Base exception for DanceIR toolbox."""
    pass


class InvalidKeypointDataError(DanceIRError):
    """Raised when keypoint data is invalid or missing."""
    pass


class AnchorExtractionError(DanceIRError):
    """Raised when anchor extraction fails."""
    pass


class ConfigurationError(DanceIRError):
    """Raised when configuration is invalid."""
    pass


class IOError(DanceIRError):
    """Raised when I/O operations fail."""
    pass

