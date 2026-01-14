"""table_diff entry point, when run as an executable."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import polars as pl

from table_diff.cli import main

pl.enable_string_cache()

VERSION = "0.2.3"

if __name__ == "__main__":
    main()
