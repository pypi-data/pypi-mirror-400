"""Constraint types for schema validation."""

from __future__ import annotations


class Len:
    """Length constraint for strings and lists.

    Examples:
        name: Annotated[str, Len(1, 50)]      # 1-50 characters
        tags: Annotated[list[str], Len(0, 10)] # 0-10 items
    """

    __slots__ = ("max", "min")

    def __init__(self, min: int = 0, max: int | None = None) -> None:
        self.min = min
        self.max = max

    def __repr__(self) -> str:
        if self.max is None:
            return f"Len({self.min})"
        return f"Len({self.min}, {self.max})"


class Range:
    """Range constraint for numbers.

    Examples:
        age: Annotated[int, Range(0, 120)]        # 0-120
        score: Annotated[float, Range(0.0, 1.0)]  # 0.0-1.0
    """

    __slots__ = ("max", "min")

    def __init__(
        self, min: float | int | None = None, max: float | int | None = None
    ) -> None:
        self.min = min
        self.max = max

    def __repr__(self) -> str:
        return f"Range({self.min}, {self.max})"


class Pattern:
    """Regex pattern constraint for strings.

    Examples:
        code: Annotated[str, Pattern(r"^[A-Z]{3}$")]
    """

    __slots__ = ("pattern",)

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    def __repr__(self) -> str:
        return f"Pattern({self.pattern!r})"


class Alias:
    """Field alias for JSON serialization.

    Maps a JSON key to a different Python field name.

    Examples:
        user_name: Annotated[str, Alias("userName")]
    """

    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Alias({self.name!r})"
