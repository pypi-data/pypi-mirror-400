"""
Helper utility functions
"""

import re
from datetime import datetime
from typing import Any


def convert_instrument_type(instrument_type):
    """
    Convert string to InstrumentType enum if needed

    Args:
        instrument_type: InstrumentType enum or string representation

    Returns:
        InstrumentType: The InstrumentType enum

    Raises:
        ValueError: If the instrument type string is invalid
    """
    from .constants import InstrumentType

    if isinstance(instrument_type, str):
        try:
            return InstrumentType(instrument_type.lower())
        except ValueError:
            valid_options = [t.value for t in InstrumentType]
            raise ValueError(
                f"Invalid instrument type: {instrument_type}. Valid options: {valid_options}"
            )
    return instrument_type


def convert_time_period(time_period):
    """
    Convert string to TimePeriod enum if needed

    Args:
        time_period: TimePeriod enum or string representation

    Returns:
        TimePeriod: The TimePeriod enum

    Raises:
        ValueError: If the time period string is invalid
    """
    from .constants import TimePeriod

    if isinstance(time_period, str):
        try:
            return TimePeriod(time_period.lower())
        except ValueError:
            valid_options = [p.value for p in TimePeriod]
            raise ValueError(f"Invalid time period: {time_period}. Valid options: {valid_options}")
    return time_period


def format_currency(amount: float, currency: str = "SEK") -> str:
    """
    Format amount as currency string

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        str: Formatted currency string
    """
    return f"{amount:,.2f} {currency}"


def parse_date(date_str: str, format: str = "%Y-%m-%d") -> datetime | None:
    """
    Parse date string to datetime object

    Args:
        date_str: Date string
        format: Date format

    Returns:
        datetime or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format)
    except (ValueError, TypeError):
        return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    return filename


def parse_percentage(value: str | float) -> float:
    """
    Parse percentage value from string or float

    Args:
        value: Percentage value (e.g., "5.5%", 5.5)

    Returns:
        float: Decimal percentage value
    """
    if isinstance(value, str):
        # Remove % and whitespace
        value = value.replace("%", "").strip()
        return float(value) / 100
    return float(value)


class InfoDict(dict):
    """
    Dictionary wrapper that allows attribute-style access

    Usage:
        info = InfoDict({"name": "Avanza", "isin": "SE0012454072"})
        info.name  # Returns "Avanza"
        info.get("name")  # Also works
        info["name"]  # Also works
    """

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
