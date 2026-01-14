"""Tests for constraint helper classes."""

from __future__ import annotations

from slimschema.constraints import Alias, Len, Pattern, Range


def test_len_repr_with_min_only():
    assert repr(Len(3)) == "Len(3)"


def test_len_repr_with_min_and_max():
    assert repr(Len(3, 5)) == "Len(3, 5)"


def test_range_repr():
    assert repr(Range(1, 2)) == "Range(1, 2)"


def test_pattern_repr():
    assert repr(Pattern(r"^[A-Z]+$")) == "Pattern('^[A-Z]+$')"


def test_alias_repr():
    assert repr(Alias("userName")) == "Alias('userName')"

