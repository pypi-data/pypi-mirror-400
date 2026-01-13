"""Exceptions for aiopulsegrow."""


class PulsegrowError(Exception):
    """Base exception for aiopulsegrow."""


class PulsegrowAuthError(PulsegrowError):
    """Authentication error with Pulsegrow API."""


class PulsegrowConnectionError(PulsegrowError):
    """Connection error with Pulsegrow API."""


class PulsegrowRateLimitError(PulsegrowError):
    """Rate limit exceeded error."""
