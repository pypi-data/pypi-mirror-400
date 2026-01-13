# -*- coding: UTF-8 -*-
# @Time : 2025/12/30 16:36 
# @Author : 刘洪波

import logging
import httpx
from tenacity import (
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception,
    before_sleep_log,
)

from openai import (
    APIError,
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
    InternalServerError,
)


def should_retry(exc: Exception) -> bool:
    """Determine whether an exception should be retried.
    
    Some errors (e.g., authentication errors, context length exceeded) should not be retried.
    Network errors, rate limit errors, etc. should be retried.
    
    Args:
        exc: Exception object to evaluate.
    
    Returns:
        bool: True if should retry, False otherwise.
    """
    if isinstance(exc, APIError):
        err_code = getattr(exc, "code", "") or ""
        err_type = getattr(exc, "type", "") or ""
        if err_code in ("invalid_request_error", "context_length_exceeded") or "auth" in err_type:
            return False

    return isinstance(
        exc,
        (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
            httpx.TimeoutException,
            httpx.NetworkError,
        ),
    )


def build_retry_config(
    logger: logging.Logger,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    max_retry_delay: float = 10.0,
) -> dict:
    """Build retry configuration dictionary for tenacity library retry decorator.
    
    Args:
        logger: Logger for recording retry information.
        max_retries: Maximum number of retries, default 3.
        retry_delay: Initial retry delay in seconds, uses exponential backoff strategy, default 1.0.
        max_retry_delay: Maximum retry delay in seconds, default 10.0.
    
    Returns:
        dict: Configuration dictionary containing retry strategy with the following keys:
            - stop: Stop condition (maximum retries)
            - wait: Wait strategy (exponential backoff)
            - retry: Retry condition (based on should_retry function)
            - before_sleep: Callback before retry (logs)
            - reraise: Whether to re-raise exception
    """
    return dict(
        stop=stop_after_attempt(max_retries),
        wait=wait_random_exponential(multiplier=retry_delay, max=max_retry_delay),
        retry=retry_if_exception(should_retry),
        before_sleep=before_sleep_log(logger, logging.INFO),
        reraise=True,
    )
