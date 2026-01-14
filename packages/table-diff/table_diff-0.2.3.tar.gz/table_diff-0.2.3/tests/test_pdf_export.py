"""Helpers for exporting comparison results."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

from pathlib import Path

import pytest

from table_diff.pdf_export import export_html_to_pdf


def test_export_to_pdf_creates_file(tmp_path: Path) -> None:
    """Test that export_to_pdf successfully creates a PDF file."""
    line = "<p>Line 1: Comparison result, Line 2: Details, Line 3: Summary</p>"

    file_path = tmp_path / "output.pdf"

    export_html_to_pdf(line, file_path)

    assert file_path.exists()
    assert file_path.stat().st_size > 100


def test_export_to_pdf_raises_error_with_empty_line(tmp_path: Path) -> None:
    """Test that export_to_pdf raises a ValueError when given an empty line."""
    file_path = tmp_path / "output.pdf"
    with pytest.raises(
        ValueError,
        match=r"Cannot export an empty document to PDF\.",
    ):
        export_html_to_pdf("", file_path)
