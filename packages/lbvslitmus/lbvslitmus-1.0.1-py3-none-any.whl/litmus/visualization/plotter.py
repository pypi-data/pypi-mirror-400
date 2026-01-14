"""
Functions for visualizing benchmark results.
"""

from pathlib import Path

from .bars import plot_enrichment_factors, plot_metric_bars, plot_top_targets
from .comparison import plot_benchmark_performance, plot_model_comparison
from .distributions import (
    plot_distribution_violins,
    plot_metric_histograms,
    plot_violin_grid,
)
from .heatmaps import plot_benchmark_heatmap, plot_metric_correlation

# Re-export all plot functions for backwards compatibility
__all__ = [
    "plot_all",
    "plot_model_comparison",
    "plot_benchmark_performance",
    "plot_benchmark_heatmap",
    "plot_violin_grid",
    "plot_metric_bars",
    "plot_distribution_violins",
    "plot_enrichment_factors",
    "plot_metric_correlation",
    "plot_metric_histograms",
    "plot_top_targets",
]


def plot_all(
    results,
    output_dir: str = "plots",
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Generate all available plots from benchmark results.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results. Can be:
        - BenchmarkResults object
        - pandas DataFrame with columns: benchmark, model, target, metric, score, (optional) seed
        - Path to CSV file with results
    output_dir : str, default="plots"
        Directory to save plots
    style : str, default="whitegrid"
        Seaborn style to use
    figure_dpi : int, default=100
        DPI for figure display
    savefig_dpi : int, default=300
        DPI for saved figures
    font_size : int, default=10
        Base font size for plots

    Examples
    --------
    >>> from litmus.benchmarking import Benchmark, BenchmarkResults
    >>> from litmus.visualization import plot_all
    >>>
    >>> # Run benchmark
    >>> results = benchmark.run()
    >>>
    >>> # Generate all plots
    >>> plot_all(results, output_dir="plots")
    >>>
    >>> # Or generate specific plots
    >>> plot_model_comparison(results, output_dir="plots")
    >>> plot_benchmark_heatmap(results, output_dir="plots")
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"Generating plots in {output_path}...")

    common_kwargs = {
        "output_dir": output_dir,
        "style": style,
        "figure_dpi": figure_dpi,
        "savefig_dpi": savefig_dpi,
        "font_size": font_size,
    }

    plot_model_comparison(results, **common_kwargs)
    plot_benchmark_performance(results, **common_kwargs)
    plot_benchmark_heatmap(results, **common_kwargs)
    plot_violin_grid(results, **common_kwargs)
    plot_metric_bars(results, **common_kwargs)
    plot_distribution_violins(results, **common_kwargs)
    plot_enrichment_factors(results, **common_kwargs)
    plot_metric_correlation(results, **common_kwargs)
    plot_metric_histograms(results, **common_kwargs)
    plot_top_targets(results, **common_kwargs)

    print(f"\n✓ All plots saved to: {output_path}")
