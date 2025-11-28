"""Retry handler with exponential backoff for Google ADK API calls."""

import asyncio
import logging
import os
import random
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _get_retry_config() -> dict[str, Any]:
    """
    Get retry configuration from environment variables with defaults.

    Returns:
        Dictionary with retry configuration
    """
    return {
        "max_retries": int(os.getenv("ADK_MAX_RETRIES", "5")),
        "initial_backoff": float(os.getenv("ADK_INITIAL_BACKOFF_SECONDS", "0.5")),
        "max_backoff": float(os.getenv("ADK_MAX_BACKOFF_SECONDS", "32.0")),
        "multiplier": float(os.getenv("ADK_BACKOFF_MULTIPLIER", "2.0")),
        "enabled": os.getenv("ADK_ENABLE_RETRY", "true").lower() == "true",
    }


def _is_retryable_error(error: Exception) -> bool:
    """
    Check if an error is retryable (5xx errors, network errors).

    Args:
        error: Exception to check

    Returns:
        True if error is retryable, False otherwise
    """
    # Check for Google API Core exceptions
    try:
        from google.api_core import exceptions as google_exceptions

        # Check for specific retryable exceptions
        if isinstance(error, (
            google_exceptions.ServiceUnavailable,
            google_exceptions.InternalServerError,
            google_exceptions.BadGateway,
            google_exceptions.GatewayTimeout,
            google_exceptions.TooManyRequests,  # 429 is retryable
        )):
            return True

        # Check for generic GoogleAPIError with status code >= 500
        if hasattr(error, "code") and error.code >= 500:
            return True
        if hasattr(error, "status_code") and error.status_code >= 500:
            return True
    except ImportError:
        # google.api_core not available, check other patterns
        pass

    # Check for network errors
    if isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return True

    # Check for HTTP errors with status code in error message or attributes
    error_str = str(error).lower()
    if any(code in error_str for code in ["503", "500", "502", "504", "429"]):
        return True

    # Check if error has status_code attribute >= 500
    if hasattr(error, "status_code") and isinstance(error.status_code, int):
        return error.status_code >= 500

    return False


def _calculate_backoff_delay(attempt: int, config: dict[str, Any]) -> float:
    """
    Calculate exponential backoff delay with jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration

    Returns:
        Delay in seconds
    """
    initial = config["initial_backoff"]
    multiplier = config["multiplier"]
    max_backoff = config["max_backoff"]

    # Calculate exponential delay
    delay = min(initial * (multiplier ** attempt), max_backoff)

    # Add jitter (10% random variation)
    jitter = random.uniform(0, delay * 0.1)
    total_delay = delay + jitter

    return total_delay


async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: Optional[int] = None,
    initial_backoff: Optional[float] = None,
    max_backoff: Optional[float] = None,
    multiplier: Optional[float] = None,
    enabled: Optional[bool] = None,
    context: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_retries: Maximum number of retries (overrides env var)
        initial_backoff: Initial backoff delay in seconds (overrides env var)
        max_backoff: Maximum backoff delay in seconds (overrides env var)
        multiplier: Backoff multiplier (overrides env var)
        enabled: Enable/disable retry (overrides env var)
        context: Additional context for logging (e.g., session_id, user_id)
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        Last exception if all retries are exhausted
    """
    # Get configuration (env vars with optional overrides)
    config = _get_retry_config()
    if max_retries is not None:
        config["max_retries"] = max_retries
    if initial_backoff is not None:
        config["initial_backoff"] = initial_backoff
    if max_backoff is not None:
        config["max_backoff"] = max_backoff
    if multiplier is not None:
        config["multiplier"] = multiplier
    if enabled is not None:
        config["enabled"] = enabled

    # If retry is disabled, just call the function once
    if not config["enabled"]:
        return await func(*args, **kwargs)

    context = context or {}
    last_error = None

    for attempt in range(config["max_retries"] + 1):
        try:
            result = await func(*args, **kwargs)
            # If we succeed and this wasn't the first attempt, log success
            if attempt > 0:
                logger.info(
                    f"Retry succeeded after {attempt} attempt(s)",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": config["max_retries"],
                        **context,
                    },
                )
            return result
        except Exception as e:
            last_error = e

            # Check if error is retryable
            if not _is_retryable_error(e):
                logger.warning(
                    f"Non-retryable error encountered: {type(e).__name__}: {e}",
                    extra={"error_type": type(e).__name__, **context},
                )
                raise

            # If this is the last attempt, don't wait, just raise
            if attempt >= config["max_retries"]:
                logger.error(
                    f"All retry attempts exhausted ({config['max_retries'] + 1} total)",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": config["max_retries"],
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        **context,
                    },
                )
                raise

            # Calculate delay and wait before retrying
            # For 429 errors, use longer initial delay to allow rate limit to reset
            is_rate_limit = (
                "429" in str(e).lower()
                or "too many requests" in str(e).lower()
                or "rate limit" in str(e).lower()
                or (hasattr(e, "status_code") and e.status_code == 429)
            )
            
            if is_rate_limit:
                # For rate limiting, use a longer initial delay
                # This gives the rate limit window time to reset
                delay = max(
                    _calculate_backoff_delay(attempt, config),
                    config["initial_backoff"] * 2  # At least 2x initial backoff for rate limits
                )
                logger.warning(
                    f"Rate limit encountered (attempt {attempt + 1}/{config['max_retries'] + 1}): "
                    f"{type(e).__name__}: {e}. Waiting {delay:.2f}s before retry to allow rate limit reset",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": config["max_retries"],
                        "delay_seconds": delay,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "is_rate_limit": True,
                        **context,
                    },
                )
            else:
                delay = _calculate_backoff_delay(attempt, config)
                logger.warning(
                    f"Retryable error encountered (attempt {attempt + 1}/{config['max_retries'] + 1}): "
                    f"{type(e).__name__}: {e}. Retrying in {delay:.2f}s",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": config["max_retries"],
                        "delay_seconds": delay,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        **context,
                    },
                )

            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Retry handler reached unexpected state")

