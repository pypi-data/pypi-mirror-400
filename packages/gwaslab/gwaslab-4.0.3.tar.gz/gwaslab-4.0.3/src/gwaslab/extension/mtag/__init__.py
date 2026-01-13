"""
MTAG (Multi-trait Analysis of GWAS) Extension Module

This module provides MTAG functionality for gwaslab, including both
command-line wrapper and refactored polars-based implementation.
"""

from ._run_mtag2 import _run_mtag2

__all__ = [
    "_run_mtag2",
]









