"""Litmus - A platform for ligand-based virtual screening.

Litmus is a modern platform for evaluating algorithms in ligand-based virtual screening.
It provides tools for downloading datasets, preprocessing molecular data, training ML models,
and evaluating screening performance.
"""

from litmus.visualization import (
    plot_all,
    plot_benchmark_heatmap,
    plot_benchmark_performance,
    plot_model_comparison,
)

__all__ = [
    "plot_all",
    "plot_model_comparison",
    "plot_benchmark_performance",
    "plot_benchmark_heatmap",
]
