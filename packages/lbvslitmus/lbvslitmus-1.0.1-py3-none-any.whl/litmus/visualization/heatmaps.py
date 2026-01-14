"""
Heatmap and correlation plots.
"""

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import seaborn as sns

from .constants import CORRELATION_METRICS, HEATMAP_METRICS
from .utils import (
    get_metric_subset,
    heatmap_bounds,
    load_results,
    plotting_context,
    save_plot,
)


def plot_benchmark_heatmap(
    results,
    output_dir: str = "plots",
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Heatmap showing average scores per benchmark and metric for each model.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    style : str, default="whitegrid"
        Seaborn style to use
    figure_dpi : int, default=100
        DPI for figure display
    savefig_dpi : int, default=300
        DPI for saved figures
    font_size : int, default=10
        Base font size for plots
    """
    with plotting_context(style, figure_dpi, savefig_dpi, font_size):
        df = load_results(results)
        df_filtered = get_metric_subset(
            df, HEATMAP_METRICS, "No data for benchmark heatmap"
        )

        if df_filtered is None:
            return

        models = sorted(df_filtered["model"].unique())
        benchmarks = sorted(df_filtered["benchmark"].unique())

        fig, axes = plt.subplots(1, len(models), figsize=(12 * len(models), 8))

        if len(models) == 1:
            axes = [axes]

        for model_idx, model in enumerate(models):
            ax = axes[model_idx]
            model_data = df_filtered[df_filtered["model"] == model]

            pivot_data = model_data.pivot_table(
                index="benchmark", columns="metric", values="score", aggfunc="mean"
            )

            available_metrics = [m for m in HEATMAP_METRICS if m in pivot_data.columns]

            if not available_metrics:
                ax.axis("off")
                ax.set_title(
                    f"{model} - Performance Heatmap (no data)",
                    fontsize=14,
                    fontweight="bold",
                    pad=20,
                )
                continue

            pivot_data = pivot_data[available_metrics]
            pivot_data = pivot_data.reindex(benchmarks)

            vmin, vmax = heatmap_bounds(pivot_data, available_metrics)

            sns.heatmap(
                pivot_data,
                annot=True,
                fmt=".3f",
                cmap="YlOrRd",
                ax=ax,
                cbar_kws={"label": "Score"},
                vmin=vmin,
                vmax=vmax,
                linewidths=0.5,
                linecolor="gray",
            )

            ax.set_title(
                f"{model} - Performance Heatmap", fontsize=14, fontweight="bold", pad=20
            )
            ax.set_xlabel("Metric", fontsize=11)
            ax.set_ylabel("Benchmark", fontsize=11)
            ax.tick_params(axis="x", rotation=45, labelsize=9)
            ax.tick_params(axis="y", rotation=0, labelsize=9)

        save_plot(output_dir, "benchmark_heatmap.png")


def plot_metric_correlation(
    results,
    output_dir: str = "plots",
    metrics: Optional[Sequence[str]] = None,
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create side-by-side correlation heatmaps for different models.

    Shows the correlation between different metrics for each model.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    metrics : Sequence[str], optional
        List of metrics to include. Defaults to CORRELATION_METRICS
    style : str, default="whitegrid"
        Seaborn style to use
    figure_dpi : int, default=100
        DPI for figure display
    savefig_dpi : int, default=300
        DPI for saved figures
    font_size : int, default=10
        Base font size for plots
    """
    with plotting_context(style, figure_dpi, savefig_dpi, font_size):
        df = load_results(results)
        metrics_to_use = metrics if metrics is not None else CORRELATION_METRICS
        df_filtered = get_metric_subset(
            df, metrics_to_use, "No data for metric correlation"
        )

        if df_filtered is None:
            return

        models = sorted(df_filtered["model"].unique())
        n_models = len(models)

        fig, axes = plt.subplots(1, n_models, figsize=(8 * n_models, 7))

        if n_models == 1:
            axes = [axes]

        for idx, model in enumerate(models):
            ax = axes[idx]
            model_data = df_filtered[df_filtered["model"] == model]

            # Pivot to get metrics as columns for each target
            pivot_data = model_data.pivot_table(
                index=["benchmark", "target"],
                columns="metric",
                values="score",
                aggfunc="mean",
            )

            available_metrics = [m for m in metrics_to_use if m in pivot_data.columns]
            if len(available_metrics) < 2:
                ax.text(
                    0.5,
                    0.5,
                    "Not enough metrics",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"Metric Correlation - {model}")
                continue

            pivot_data = pivot_data[available_metrics].dropna()
            corr_matrix = pivot_data.corr()

            sns.heatmap(
                corr_matrix,
                annot=True,
                fmt=".2f",
                cmap="RdBu_r",
                ax=ax,
                center=0,
                vmin=-1,
                vmax=1,
                square=True,
                linewidths=0.5,
                cbar_kws={"label": "Correlation"},
            )

            ax.set_title(
                f"Metric Correlation - {model}", fontsize=12, fontweight="bold"
            )
            ax.tick_params(axis="x", rotation=45)
            ax.tick_params(axis="y", rotation=0)

        save_plot(output_dir, "metric_correlation.png")
