"""Dataset helpers: conversion utilities between raw rows and Pydantic models.

This module contains small conversion helpers used when loading tabular or
line-oriented datasets into the project's Pydantic models.
"""

from .schemas import TextRecord


def row_to_textrecord(row: dict) -> TextRecord:
    """Convert a mapping (row) to a `TextRecord` instance.

    Args:
        row: A mapping with keys 'text', 'source', 'title', 'line_number'.

    Returns:
        A validated ``TextRecord`` constructed from the row values.
    """
    return TextRecord(
        text=row["text"],
        source=row["source"],
        title=row["title"],
        line_number=int(row["line_number"]),
    )
