"""
Retry logic with exponential backoff for LLM API calls.

Implements OpenAI's recommended retry pattern with configurable exponential backoff.
"""
import asyncio
from typing import TypeVar, Callable, Any, Awaitable
from loguru import logger

T = TypeVar('T')


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    max_retries: int,
    retry_delay: float,
    backoff_multiplier: float,
    retry_enabled: bool,
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Execute async function with exponential backoff retry logic.

    Follows OpenAI's recommended retry pattern:
    - Attempt 1: Immediate call
    - Attempt 2: retry_delay seconds (default: 1s)
    - Attempt 3: retry_delay * backoff_multiplier seconds (default: 2s)
    - Attempt 4: retry_delay * backoff_multiplier^2 seconds (default: 4s)

    Args:
        func: Async function to execute with retry logic
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        retry_enabled: Whether retry logic is enabled (default: False)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from successful function execution

    Raises:
        Exception: If all retry attempts fail, raises the last exception encountered

    Example:
        result = await retry_with_backoff(
            my_api_call,
            max_retries=3,
            retry_delay=1.0,
            backoff_multiplier=2.0,
            retry_enabled=True,
            api_key="...",
            model="gpt-4"
        )
    """
    if not retry_enabled:
        return await func(*args, **kwargs)

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            # Don't retry on the last attempt
            if attempt == max_retries:
                logger.error(f"Request failed after {max_retries + 1} attempts: {str(e)}")
                raise

            # Calculate delay with exponential backoff
            delay = retry_delay * (backoff_multiplier ** attempt)
            logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")

            await asyncio.sleep(delay)

    # This shouldn't be reached, but just in case
    raise last_exception or Exception("Request failed with unknown error")
