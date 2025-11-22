"""
Retry and fallback handler for API calls.
"""
import time
import random
from typing import Callable, Any, Dict, Optional, List
from functools import wraps

from ..utils.logging import get_logger


logger = get_logger("RetryHandler")


class RetryHandler:
    """Handles retry logic with exponential backoff and fallback providers."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to prevent thundering herd
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add random jitter (0-25% of delay)
            jitter_amount = delay * 0.25 * random.random()
            delay += jitter_amount
        
        return delay


class FallbackProvider:
    """Manages fallback between multiple service providers."""
    
    def __init__(self, providers: List[Callable], provider_names: Optional[List[str]] = None):
        """
        Initialize fallback provider.
        
        Args:
            providers: List of provider functions (in order of preference)
            provider_names: Optional names for logging
        """
        self.providers = providers
        self.provider_names = provider_names or [f"Provider{i+1}" for i in range(len(providers))]
        self.current_provider_index = 0
        self.logger = get_logger("FallbackProvider")
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute with fallback to next provider on failure.
        
        Args:
            *args: Positional arguments for provider functions
            **kwargs: Keyword arguments for provider functions
        
        Returns:
            Result from first successful provider
        
        Raises:
            Exception: If all providers fail
        """
        last_exception = None
        
        for idx, provider in enumerate(self.providers):
            provider_name = self.provider_names[idx]
            
            try:
                self.logger.info(f"Attempting with {provider_name}")
                result = provider(*args, **kwargs)
                self.logger.info(f"Success with {provider_name}")
                self.current_provider_index = idx
                return result
            except Exception as e:
                last_exception = e
                self.logger.warning(f"{provider_name} failed: {e}")
                
                if idx < len(self.providers) - 1:
                    self.logger.info(f"Falling back to next provider...")
                else:
                    self.logger.error("All providers failed")
        
        raise last_exception
    
    def get_current_provider(self) -> str:
        """Get name of currently active provider."""
        return self.provider_names[self.current_provider_index]


def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum retry attempts
        base_delay: Base delay in seconds
    """
    def decorator(func: Callable) -> Callable:
        handler = RetryHandler(max_retries=max_retries, base_delay=base_delay)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.retry(func, *args, **kwargs)
        
        return wrapper
    return decorator

