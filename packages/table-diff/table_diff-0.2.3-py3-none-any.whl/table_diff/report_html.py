"""Tool for generating an HTML report representing the differences between two tables."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Parker L

from pathlib import Path
from typing import Any

import minify_html
from jinja2 import Environment, FileSystemLoader, select_autoescape

from table_diff.df_helpers import df_to_html
from table_diff.report_common import DiffEvaluation


def _prepare_html_context(diff: DiffEvaluation) -> dict[str, Any]:
    return {
        "old_filename": diff.old_filename,
        "new_filename": diff.new_filename,
        "unique_key": diff.unique_key,
        "general_observations": diff.general_observations,
        "compare_cols": diff.compare_cols_result,
        "compare_rows": diff.compare_unique_key_result,
        "df_old_rows_count": diff.df_old.height,
        "df_new_rows_count": diff.df_new.height,
        "column_diffs": list(diff.column_diffs.values()),
    }


def generate_html_report(
    diff_evaluation: DiffEvaluation,
    *,
    minify_output_html: bool = True,
    enable_simple_pdf_mode: bool = False,
) -> str:
    """Generate an HTML report of the differences between two tables.

    Returns:
        A string containing the HTML representation of the differences between the two tables.

    """
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "html_template"),
        autoescape=select_autoescape(["html"]),
    )

    # Make helpers available in templates.
    env.filters["pct"] = lambda x: f"{x:.1%}"

    template = env.get_template("table_diff_report.html.jinja2")
    html = template.render(
        **_prepare_html_context(diff_evaluation),
        df_to_html=df_to_html,
        enable_simple_pdf_mode=enable_simple_pdf_mode,
    )

    if enable_simple_pdf_mode:
        # Strip certain tags. Important mostly for TOC generation.
        for tag in ("details", "summary"):
            html = html.replace(f"<{tag}>", "").replace(f"</{tag}>", "")

        # Remove block-inline that breaks the table of contents in simple PDF mode.
        html = html.replace('class="display-inline-block"', "")

    if minify_output_html is True:
        # Minify HTML output to save disk storage space (e.g., if emailing/sending it).
        html = minify_html.minify(
            html,
            minify_js=True,
            minify_css=True,
            keep_html_and_head_opening_tags=True,
        )

    return html
