"""
LLM Adapter Exceptions.

Typed exceptions for LLM adapter errors.
"""

from __future__ import annotations


class LLMError(Exception):
    """Base exception for LLM adapter errors."""

    pass


class LLMTimeoutError(LLMError):
    """LLM request timed out."""

    pass


class LLMInvalidResponseError(LLMError):
    """LLM response was not valid structured output."""

    pass


class LLMProviderError(LLMError):
    """Provider-specific error (API error, network, etc.)."""

    pass


class LLMCredentialsError(LLMError):
    """Missing or invalid API credentials."""

    pass


class LLMRateLimitError(LLMError):
    """Rate limit exceeded."""

    pass
