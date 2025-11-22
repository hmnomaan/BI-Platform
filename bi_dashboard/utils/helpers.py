"""
Helper utilities for BI Dashboard.
"""
from loguru import logger
from typing import Any, Optional


def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)


def format_number(value: Any, decimals: int = 2) -> str:
    """Format a number with specified decimal places."""
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_currency(value: Any, currency: str = "USD") -> str:
    """Format a number as currency."""
    try:
        if currency == "USD":
            return f"${float(value):,.2f}"
        else:
            return f"{currency} {float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Any, decimals: int = 1) -> str:
    """Format a number as percentage."""
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

