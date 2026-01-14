# Copyright 2023-2025 Luminary Cloud, Inc. All Rights Reserved.
from datetime import datetime


def parse_iso_datetime(iso_str: str) -> datetime:
    """
    Parse an ISO format datetime string, handling 'Z' timezone indicator.

    This function acts as a compatibility shim for Python < 3.11, which doesn't
    support 'Z' in fromisoformat. It normalizes 'Z' (or 'z') to '+00:00' before parsing,
    making it compatible with all Python versions (3.7+).

    Parameters
    ----------
    iso_str : str
        ISO format datetime string, optionally ending with 'Z' or 'z' for UTC.

    Returns
    -------
    datetime
        Parsed datetime object.

    Raises
    ------
    ValueError
        If the string is not a valid ISO format datetime string.
    TypeError
        If iso_str is not a string.

    Examples
    --------
    >>> parse_iso_datetime("2023-07-31T13:54:12Z")
    datetime.datetime(2023, 7, 31, 13, 54, 12, tzinfo=datetime.timezone.utc)
    >>> parse_iso_datetime("2023-07-31T13:54:12+00:00")
    datetime.datetime(2023, 7, 31, 13, 54, 12, tzinfo=datetime.timezone.utc)
    """
    if not isinstance(iso_str, str):
        raise TypeError(f"parse_iso_datetime expects a string, got {type(iso_str).__name__}")

    if not iso_str:
        raise ValueError("parse_iso_datetime: empty string is not a valid ISO format datetime")

    # Normalize 'Z' or 'z' at the end to '+00:00'
    # Strip whitespace first to handle cases like "2023-01-01T00:00:00Z "
    iso_str = iso_str.strip()

    if iso_str.endswith(("Z", "z")):
        # Only normalize if the string is longer than just 'Z'/'z'
        if len(iso_str) > 1:
            iso_str = iso_str[:-1] + "+00:00"
        else:
            raise ValueError("parse_iso_datetime: 'Z' alone is not a valid ISO format datetime")

    return datetime.fromisoformat(iso_str)
