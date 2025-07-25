"""Custom exceptions for the MixBridge calculator system."""

class MixBridgeError(Exception):
    """Base exception for all MixBridge errors."""
    pass

class ValidationError(MixBridgeError):
    """Raised when data validation fails."""
    pass

class ConfigurationError(MixBridgeError):
    """Raised when configuration is invalid or missing."""
    pass

class CalculationError(MixBridgeError):
    """Raised when calculations fail or produce invalid results."""
    pass

class DataProcessingError(MixBridgeError):
    """Raised when data processing operations fail."""
    pass

class FileOperationError(MixBridgeError):
    """Raised when file read/write operations fail."""
    pass

class InvalidMetricError(MixBridgeError):
    """Raised when an invalid metric is requested."""
    pass

class InsufficientDataError(MixBridgeError):
    """Raised when there's not enough data to perform calculations."""
    pass