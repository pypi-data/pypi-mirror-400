r"""Contain types used in the remaining of the package."""

from __future__ import annotations

__all__ = ["SORT_KINDS", "SortKind"]

from typing import Literal

SortKind = Literal["quicksort", "mergesort", "heapsort", "stable"]
SORT_KINDS: list[SortKind] = ["quicksort", "mergesort", "heapsort", "stable"]
