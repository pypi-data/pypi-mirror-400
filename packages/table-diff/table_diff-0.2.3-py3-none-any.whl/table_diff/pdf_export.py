"""Helpers for exporting comparison results."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

# pyright: basic
# pymupdf has very bad typing, so we just use basic pyright here.

from pathlib import Path
from typing import Any


def export_html_to_pdf(html_content: str, pdf_file_path: Path) -> None:  # noqa: C901
    """Write the input HTML document to a PDF.

    Args:
        html_content (str): The comparison result to export.
        pdf_file_path (str): The path to save the results to.

    Raises:
        ImportError: If the required module is not installed.
        ValueError: If the line is empty.
        PermissionError: If the file cannot be overwritten.

    """
    try:
        import pymupdf  # pyright: ignore[reportMissingTypeStubs] # noqa: PLC0415
    except ImportError as err:
        msg = (
            'Trying to export a PDF. Cannot import the module "pymupdf". '
            "Consider re-installing table_diff with the optional feature: "
            "`uv tool install table_diff --with pymupdf`."
        )
        raise ImportError(msg) from err

    if not html_content:
        msg = "Cannot export an empty document to PDF."
        raise ValueError(msg)

    if pdf_file_path.suffix != ".pdf":
        msg = "The file path should end with '.pdf'."
        raise ValueError(msg)

    # Check if file exists and try to remove it.
    if pdf_file_path.exists():
        try:
            pdf_file_path.unlink()
        except PermissionError as err:
            msg = f"Cannot overwrite the file: {pdf_file_path}. It might be open in a viewer."
            raise PermissionError(msg) from err

    story = pymupdf.Story(html=html_content)
    media_box: pymupdf.Rect = pymupdf.paper_rect("A3")  # Paper size.

    # Table of contents (TOC) state management.
    toc: list[tuple[int, str, int]] = []
    page_num = 0

    def recorder(element_position: Any) -> None:  # noqa: ANN401
        """Store table of contents. Callback invoked by `s`."""
        nonlocal page_num

        # Only consider opening tags.
        if not element_position.open_close & 1:
            return

        # element_position.heading is 0 if not a header, otherwise 1..6
        if element_position.heading:
            toc.append(
                (
                    element_position.heading,  # TOC level
                    element_position.text.strip(),  # Heading text
                    page_num,  # Page number (1-based)
                )
            )

    story = pymupdf.Story(html=html_content)
    media_box: pymupdf.Rect = pymupdf.paper_rect("A3")

    # Add margins.
    where = media_box

    with pymupdf.DocumentWriter(pdf_file_path) as writer:
        more = True
        while more:
            page_num += 1
            device = writer.begin_page(media_box)
            more, _filled = story.place(where)

            # Store TOC entries.
            story.element_positions(recorder)

            # Write to the page.
            story.draw(device)
            writer.end_page()

    # Add TOC to PDF.
    if toc:
        with pymupdf.open(pdf_file_path) as doc:
            doc.set_toc(toc)
            doc.saveIncr()
