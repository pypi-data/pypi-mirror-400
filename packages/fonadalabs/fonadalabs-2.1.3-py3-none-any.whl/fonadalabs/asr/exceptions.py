# fonada_asr/exceptions.py

class ASRSDKError(Exception):
    """Base exception for the SDK."""


class ConfigurationError(ASRSDKError):
    """Raised when the SDK configuration is invalid."""


class ValidationError(ASRSDKError):
    """Raised when input validation fails (e.g., invalid language)."""


class AuthenticationError(ASRSDKError):
    """Raised for 401/403 API key issues."""


class HTTPRequestError(ASRSDKError):
    """Raised when an HTTP request fails at network level."""


class ServerError(ASRSDKError):
    """Raised when the server returns 5xx."""


class RateLimitError(ASRSDKError):
    """Raised when the server returns a 429 rate-limit response."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
        self.rate_limit = details.get("rate_limit") if details else None
        self.current_usage = details.get("current_usage") if details else None
        self.remaining = details.get("remaining") if details else None
        self.reset_at = details.get("reset_at") if details else None
        self.retry_after_seconds = details.get("retry_after_seconds") if details else None
        self.rate_period = details.get("rate_period") if details else None


class TimeoutError(ASRSDKError):
    """Raised when a request exceeds timeout."""


class CreditsExhaustedError(ASRSDKError):
    """Raised when API credits are exhausted."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
        self.current_usage = details.get("current_usage") if details else None
        self.credit_limit = details.get("credit_limit") if details else None
        self.remaining_balance = details.get("remaining_balance") if details else None
        self.estimated_cost = details.get("estimated_cost") if details else None
        self.billing_cycle_end = details.get("billing_cycle_end") if details else None
        self.tier = details.get("tier") if details else None
