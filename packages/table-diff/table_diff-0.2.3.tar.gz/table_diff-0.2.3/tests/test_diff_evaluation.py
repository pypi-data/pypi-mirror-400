"""Unit tests for the `DiffEvaluation` class."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

from pathlib import Path
from typing import Literal

import polars as pl
import pytest

from table_diff.pdf_export import export_html_to_pdf
from table_diff.report_common import DiffEvaluation
from table_diff.report_duckdb import export_duckdb_report
from table_diff.report_html import generate_html_report
from table_diff.report_markdown import generate_markdown_report


def test_diff_evaluation_runs() -> None:
    """Test that DiffEvaluation.evaluate runs without error on sample data."""
    data_folder = Path(__file__).parent / "demo_datasets/populations"
    assert data_folder.is_dir()

    df_old = pl.read_csv(path_old := data_folder / "city-populations_2010.csv")
    df_new = pl.read_csv(path_new := data_folder / "city-populations_2015.csv")

    _ = DiffEvaluation.evaluate(
        df_old,
        df_new,
        unique_key=["location_id"],
        old_filename=path_old.name,
        new_filename=path_new.name,
    )


@pytest.mark.parametrize("force_sample_mode", ["normal", "force_sample"])
def test_diff_evaluation_and_conversions_run(
    tmp_path: Path, force_sample_mode: Literal["normal", "force_sample"]
) -> None:
    """Test that DiffEvaluation and report exports run without error on sample data.

    This test is more of an integration test than a unit test, as it checks many functions
    sequentially.
    """
    data_folder = Path(__file__).parent / "demo_datasets/populations"
    assert data_folder.is_dir()

    df_old = pl.read_csv(path_old := data_folder / "city-populations_2010.csv")
    df_new = pl.read_csv(path_new := data_folder / "city-populations_2015.csv")

    diff_evaluation = DiffEvaluation.evaluate(
        df_old,
        df_new,
        unique_key=["location_id"],
        old_filename=path_old.name,
        new_filename=path_new.name,
    )

    if force_sample_mode == "force_sample":
        # Force pretending it's a large dataset, and thus just a sample is used.
        diff_evaluation.column_diffs["population"].df_diff_full = None

    md_report = generate_markdown_report(diff_evaluation)
    assert len(md_report) > 1000

    html_report_general = generate_html_report(diff_evaluation, enable_simple_pdf_mode=False)
    assert len(html_report_general) > 1000

    html_report_for_pdf = generate_html_report(diff_evaluation, enable_simple_pdf_mode=True)
    assert len(html_report_for_pdf) > 1000

    export_html_to_pdf(html_report_for_pdf, tmp_path / "report.pdf")
    export_duckdb_report(diff_evaluation, tmp_path / "report.duckdb")
