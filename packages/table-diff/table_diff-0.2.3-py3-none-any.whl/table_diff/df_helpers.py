"""Helpers for working with Polars DataFrames."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import html
from typing import Literal

import polars as pl


def assert_unique_key(
    df: pl.DataFrame,
    unique_key: list[str] | str,
) -> None:
    """Assert that all rows of `unique_key` are unique.

    Args:
        df: The DataFrame to check.
        unique_key: The column(s) that should be unique.

    Raises:
        AssertionError: If the check fails.

    """
    if isinstance(unique_key, str):
        unique_key = [unique_key]

    df_grouped = (
        df.group_by(unique_key)
        .agg(
            rows_with_this_key=pl.len(),
        )
        .filter(  # pyright: ignore[reportUnknownMemberType]
            pl.col("rows_with_this_key") > pl.lit(1),
        )
    )
    problem_row_count = df_grouped.height

    if problem_row_count > 0:
        msg = f"{problem_row_count:,}/{df.height:,} rows are not unique"
        raise AssertionError(msg)


def is_key_unique(
    df: pl.DataFrame,
    unique_key: list[str] | str,
) -> bool:
    """Check if all rows of `unique_key` are unique.

    Args:
        df: The DataFrame to check.
        unique_key: The column(s) that should be unique.

    Returns:
        bool: True if all rows are unique, False otherwise.

    """
    if isinstance(unique_key, str):
        unique_key = [unique_key]

    df_grouped = (
        df.group_by(unique_key)
        .agg(
            rows_with_this_key=pl.len(),
        )
        .filter(  # pyright: ignore[reportUnknownMemberType]
            pl.col("rows_with_this_key") > pl.lit(1),
        )
    )
    problem_row_count = df_grouped.height

    return problem_row_count == 0


def assert_col_has_no_nulls(df: pl.DataFrame, col: str) -> None:
    """Assert that the supplied column has no null values.

    Args:
        df: The DataFrame to check.
        col: The column to check.

    Raises:
        AssertionError: If the check fails.

    """
    non_null_count = df[col].count()
    null_count = df.height - non_null_count
    if null_count > 0:
        msg = f"{null_count:,}/{df.height:,} values in column are null"
        raise AssertionError(msg)


def df_to_markdown(
    df: pl.DataFrame,
    *,
    show_types: bool = True,
    show_shape: bool = True,
    table_cell_alignment: Literal["LEFT", "CENTER", "RIGHT"] = "CENTER",
) -> str:
    """Convert a DataFrame to a markdown table.

    Returns:
        A markdown table string.

    """
    with pl.Config() as cfg:
        cfg.set_tbl_formatting("ASCII_MARKDOWN")
        cfg.set_tbl_hide_dataframe_shape(True)

        if show_types:
            cfg.set_tbl_column_data_type_inline(True)
        else:
            cfg.set_tbl_hide_column_data_types(True)

        cfg.set_tbl_cell_alignment(table_cell_alignment)

        md = str(df)

    # If the markdown starts with two lines of headers, then we must regenerate without types.
    if show_types:
        md_lines = md.splitlines()
        if md_lines[0].startswith("| ") and md_lines[1].startswith("| "):
            md = df_to_markdown(
                df,
                show_types=False,  # Force.
                show_shape=False,  # Force false, otherwise it may be added twice.
                table_cell_alignment=table_cell_alignment,
            )

    # Manually re-add the shape nicely.
    if show_shape:
        md = f"Table size: {df.height:,} rows x {df.width:,} columns\n\n" + md

    return md


def df_to_html(
    df: pl.DataFrame,
    *,
    max_rows: int | None = 20,
    show_shape: bool = False,
    show_types: bool = True,
    max_cell_length: int | None = 1000,
) -> str:
    """Convert a Polars DataFrame to a plain HTML table.

    Returns:
        A string containing the HTML representation of the DataFrame.

    """
    if df.is_empty():
        return '<p class="muted">No rows to display.</p>'

    original_height = df.height
    if max_rows is not None:
        df = df.head(max_rows)

    columns = df.columns
    rows = df.rows()

    out: list[str] = []

    if show_shape:
        out.append(f'<p class="muted">Shape: {original_height:,} rows x {df.width} columns</p>')

    out.extend(("<table>", "<thead><tr>"))
    if show_types:
        out.extend(
            f'<th>{html.escape(col)}<br><span class="muted">{html.escape(str(dtype))}</span></th>'
            for col, dtype in df.schema.items()
        )
    else:
        out.extend(f"<th>{html.escape(str(col))}</th>" for col in columns)
    out.extend(("</tr></thead>", "<tbody>"))

    for row_num, row in enumerate(rows):
        # Manual nth-child replacement (required because PDF CSS doesn't support automatic
        # nth-child).
        row_class = "row-even" if row_num % 2 == 0 else "row-odd"
        out.append(f'<tr class="{row_class}">')

        for val in row:
            if val is None:
                cell = '<span class="null-cell">NULL</span>'
            else:
                val_str = str(val)
                if max_cell_length and (len(val_str) > max_cell_length):
                    val_str = val_str[:max_cell_length] + "…"
                cell = html.escape(val_str)

            out.append(f"<td>{cell}</td>")
        out.append("</tr>")

    out.extend(("</tbody>", "</table>"))
    return "\n".join(out)
