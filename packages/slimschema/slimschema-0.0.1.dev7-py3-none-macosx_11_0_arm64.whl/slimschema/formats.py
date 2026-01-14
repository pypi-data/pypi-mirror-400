"""Format marker types for common string formats.

These are used as type annotations to indicate string format requirements.

Examples:
    email: Annotated[str, Email]
    website: Annotated[str, Url]
    id: Annotated[str, Uuid]
"""

from __future__ import annotations


class Email:
    """Email format marker."""


class Url:
    """URL format marker."""


class Uuid:
    """UUID format marker."""


class Date:
    """ISO date format marker (YYYY-MM-DD)."""


class DateTime:
    """ISO datetime format marker."""
