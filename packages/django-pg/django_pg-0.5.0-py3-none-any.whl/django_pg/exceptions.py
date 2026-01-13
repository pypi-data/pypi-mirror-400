class PaymentConfigurationError(Exception):
    """Raised when required payment configuration is missing."""
    pass

class PaymentRuntimeError(Exception):
    """Errors from the payment provider (network, API, etc.)"""
    pass