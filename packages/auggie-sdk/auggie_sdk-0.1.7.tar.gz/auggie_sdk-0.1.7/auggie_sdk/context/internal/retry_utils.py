"""
Retry utilities with exponential backoff
Based on clients/sidecar/libs/src/utils/promise-utils.ts
"""

import time
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class BackoffParams:
    """Parameters for exponential backoff retry logic"""

    initial_ms: int = 100
    mult: float = 2.0
    max_ms: int = 30_000
    max_tries: Optional[int] = None
    max_total_ms: Optional[int] = None
    can_retry: Optional[Callable[[Exception], bool]] = None


def _delay_ms(ms: int) -> None:
    """Delay for the specified number of milliseconds"""
    if ms > 0:
        time.sleep(ms / 1000.0)


def is_retriable_error(e: Exception) -> bool:
    """
    Check if an error is retriable based on its properties.

    Retriable errors include:
    - Server errors (5xx status codes)
    - Specific retriable status codes (499, 503)
    """
    # Check for HTTP status codes (e.g., APIError with status attribute)
    if hasattr(e, "status"):
        status = e.status  # type: ignore

        # Match the default VSCode client retry logic:
        # - 499 (cancelled)
        # - 503 (unavailable)
        # - 5xx (unavailable)
        #
        # Note: We do NOT retry 429 or 504 by default
        # (only chat streams retry those)
        return status == 499 or status == 503 or (500 <= status < 600)

    return False


def is_chat_retriable_error(e: Exception) -> bool:
    """
    Check if an error is retriable for chat streaming endpoints.

    Chat streams retry additional status codes beyond the default retry logic:
    - 429 (rate limit)
    - 529 (overloaded)
    """
    # Check for HTTP status codes (e.g., APIError with status attribute)
    if hasattr(e, "status"):
        status = e.status  # type: ignore

        # Chat streams retry:
        # - 429 (rate limit)
        # - 499 (cancelled)
        # - 503 (unavailable)
        # - 529 (overloaded)
        # - 5xx (server errors)
        return (
            status == 429
            or status == 499
            or status == 503
            or status == 529
            or (500 <= status < 600)
        )

    return False


def retry_with_backoff(
    fn: Callable[[], T],
    debug: bool = False,
    params: Optional[BackoffParams] = None,
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        fn: The function to retry
        debug: Whether to log debug messages
        params: Backoff parameters (uses defaults if not provided)

    Returns:
        The function's return value

    Raises:
        Exception: If all retries are exhausted or error is not retriable
    """
    if params is None:
        params = BackoffParams()

    can_retry_fn = params.can_retry or is_retriable_error
    backoff_ms = 0.0
    start_time_ms = time.monotonic() * 1000

    tries = 0
    while True:
        try:
            result = fn()
            if tries > 0 and debug:
                print(f"[RetryUtils] Operation succeeded after {tries} transient failures")
            return result
        except Exception as e:
            curr_try_count = tries + 1

            # Check if we have exceeded the max number of retries
            if params.max_tries is not None and curr_try_count >= params.max_tries:
                raise

            # Check if we should retry this error
            if not can_retry_fn(e):
                raise

            # Calculate backoff delay with exponential growth
            if backoff_ms == 0:
                backoff_ms = params.initial_ms
            else:
                backoff_ms = min(backoff_ms * params.mult, params.max_ms)

            if debug:
                print(
                    f"[RetryUtils] Operation failed with error {e}, "
                    f"retrying in {backoff_ms:.0f} ms; retries = {tries}"
                )

            # Check if the backoff delay will exceed total time
            if params.max_total_ms is not None:
                elapsed_ms = time.monotonic() * 1000 - start_time_ms
                if elapsed_ms + backoff_ms > params.max_total_ms:
                    raise

            _delay_ms(int(backoff_ms))
            tries += 1


def retry_chat(
    fn: Callable[[], T],
    debug: bool = False,
    params: Optional[BackoffParams] = None,
) -> T:
    """
    Retry a chat function with exponential backoff.

    Uses chat-specific retry logic that includes additional status codes
    like 429 (rate limit) and 529 (overloaded).

    Args:
        fn: The function to retry
        debug: Whether to log debug messages
        params: Backoff parameters (uses defaults if not provided)

    Returns:
        The function's return value

    Raises:
        Exception: If all retries are exhausted
    """
    if params is None:
        params = BackoffParams()

    # Create new params with chat-specific retry logic
    chat_params = BackoffParams(
        initial_ms=params.initial_ms,
        mult=params.mult,
        max_ms=params.max_ms,
        max_tries=params.max_tries,
        max_total_ms=params.max_total_ms,
        can_retry=is_chat_retriable_error,
    )

    return retry_with_backoff(fn, debug, chat_params)

