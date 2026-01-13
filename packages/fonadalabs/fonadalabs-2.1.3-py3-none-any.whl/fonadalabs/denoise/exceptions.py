#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Denoise SDK Exceptions
"""


class DenoiseError(Exception):
    """Base exception for Denoise SDK"""
    pass


class CreditsExhaustedError(DenoiseError):
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


class RateLimitError(DenoiseError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
        self.rate_limit = details.get("rate_limit") if details else None
        self.current_usage = details.get("current_usage") if details else None
        self.remaining = details.get("remaining") if details else None
        self.reset_at = details.get("reset_at") if details else None
        self.retry_after_seconds = details.get("retry_after_seconds") if details else None
        self.rate_period = details.get("rate_period") if details else None


__all__ = ["DenoiseError", "CreditsExhaustedError", "RateLimitError"]

