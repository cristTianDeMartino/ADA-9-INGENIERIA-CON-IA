"""Custom exceptions for Customer Search feature."""


class CustomerSearchError(Exception):
    """Base exception for customer search domain errors."""
    pass


class ValidationError(CustomerSearchError):
    """Raised when search query or parameters violate validation rules (VR-01, VR-02, VR-03)."""
    pass


class DataLoadError(CustomerSearchError):
    """Raised when repository fails to load customer data from disk or malformed JSON."""
    pass
