"""
Distribution plots (violins, histograms).
"""

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .constants import DISTRIBUTION_METRICS, HISTOGRAM_METRICS, VIOLIN_GRID_METRICS
from .utils import (
    get_metric_subset,
    get_model_palette,
    load_results,
    plotting_context,
    save_plot,
)


def plot_violin_grid(
    results,
    output_dir: str = "plots",
    metrics: Optional[Sequence[str]] = None,
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create a grid of violin plots showing metric distributions across datasets and models.

    Generates a grid where rows are datasets/benchmarks and columns are metrics,
    with split violins showing different models.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    metrics : Sequence[str], optional
        List of metrics to plot. Defaults to VIOLIN_GRID_METRICS
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
        metrics_to_plot = metrics if metrics is not None else VIOLIN_GRID_METRICS
        df_filtered = get_metric_subset(df, metrics_to_plot, "No data for violin grid")

        if df_filtered is None:
            return

        benchmarks = sorted(df_filtered["benchmark"].unique())
        available_metrics = [
            m for m in metrics_to_plot if m in df_filtered["metric"].unique()
        ]
        models = sorted(df_filtered["model"].unique())

        if not benchmarks or not available_metrics:
            print("No data for violin grid")
            return

        n_rows = len(benchmarks)
        n_cols = len(available_metrics)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3 * n_rows))

        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)

        palette = get_model_palette(models)

        for row_idx, benchmark in enumerate(benchmarks):
            for col_idx, metric in enumerate(available_metrics):
                ax = axes[row_idx, col_idx]
                data = df_filtered[
                    (df_filtered["benchmark"] == benchmark)
                    & (df_filtered["metric"] == metric)
                ]

                if data.empty:
                    ax.text(
                        0.5,
                        0.5,
                        "No data",
                        ha="center",
                        va="center",
                        transform=ax.transAxes,
                    )
                else:
                    sns.violinplot(
                        data=data,
                        x="model",
                        y="score",
                        hue="model",
                        ax=ax,
                        palette=palette,
                        inner="point",
                        legend=False,
                    )

                    # Add mean markers
                    for i, model in enumerate(models):
                        model_data = data[data["model"] == model]["score"]
                        if not model_data.empty:
                            mean_val = model_data.mean()
                            ax.scatter(
                                [i], [mean_val], color="red", s=30, zorder=5, marker="D"
                            )

                if row_idx == 0:
                    ax.set_title(metric, fontsize=12, fontweight="bold")
                if col_idx == 0:
                    ax.set_ylabel(benchmark, fontsize=10, fontweight="bold")
                else:
                    ax.set_ylabel("")

                ax.set_xlabel("")
                ax.tick_params(axis="x", rotation=45, labelsize=8)

        # Add legend
        if len(models) > 1:
            handles = [
                plt.Rectangle((0, 0), 1, 1, facecolor=palette[m]) for m in models
            ]
            fig.legend(handles, models, loc="upper right", title="Model")

        save_plot(output_dir, "violin_grid.png")


def plot_distribution_violins(
    results,
    output_dir: str = "plots",
    metrics: Optional[Sequence[str]] = None,
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create violin plots showing metric distribution across benchmarks.

    Generates a 2x2 grid of violin plots (or appropriate grid size) showing
    the distribution of each metric across different benchmarks.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    metrics : Sequence[str], optional
        List of metrics to plot. Defaults to DISTRIBUTION_METRICS
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
        metrics_to_plot = metrics if metrics is not None else DISTRIBUTION_METRICS
        df_filtered = get_metric_subset(
            df, metrics_to_plot, "No data for distribution violins"
        )

        if df_filtered is None:
            return

        available_metrics = [
            m for m in metrics_to_plot if m in df_filtered["metric"].unique()
        ]
        n_metrics = len(available_metrics)
        models = sorted(df_filtered["model"].unique())
        palette = get_model_palette(models)

        n_cols = 2
        n_rows = (n_metrics + 1) // 2

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 5 * n_rows))
        axes = np.atleast_1d(axes).flatten()

        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            metric_data = df_filtered[df_filtered["metric"] == metric]

            if metric_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"{metric} - Distribution Across Benchmarks")
                continue

            sns.violinplot(
                data=metric_data,
                x="benchmark",
                y="score",
                hue="model",
                ax=ax,
                palette=palette,
                split=len(models) == 2,
                inner="quart",
            )

            ax.set_title(
                f"{metric} - Distribution Across Benchmarks",
                fontsize=12,
                fontweight="bold",
            )
            ax.set_xlabel("Benchmark", fontsize=10)
            ax.set_ylabel("Score", fontsize=10)
            ax.tick_params(axis="x", rotation=45)
            ax.legend(title="Model", fontsize=8)
            ax.grid(axis="y", alpha=0.3)

        # Hide unused axes
        for idx in range(len(available_metrics), len(axes)):
            axes[idx].axis("off")

        save_plot(output_dir, "distribution_violins.png")


def plot_metric_histograms(
    results,
    output_dir: str = "plots",
    metrics: Optional[Sequence[str]] = None,
    bins: int = 15,
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create histograms with KDE curves showing metric distributions.

    Generates overlapping histograms for each model with kernel density estimates.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    metrics : Sequence[str], optional
        List of metrics to plot. Defaults to HISTOGRAM_METRICS
    bins : int, default=15
        Number of histogram bins
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
        metrics_to_plot = metrics if metrics is not None else HISTOGRAM_METRICS
        df_filtered = get_metric_subset(df, metrics_to_plot, "No data for histograms")

        if df_filtered is None:
            return

        available_metrics = [
            m for m in metrics_to_plot if m in df_filtered["metric"].unique()
        ]
        models = sorted(df_filtered["model"].unique())
        palette = get_model_palette(models)

        n_metrics = len(available_metrics)
        n_cols = 3
        n_rows = (n_metrics + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
        axes = np.atleast_1d(axes).flatten()

        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            metric_data = df_filtered[df_filtered["metric"] == metric]

            if metric_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(metric)
                continue

            for model in models:
                model_data = metric_data[metric_data["model"] == model]["score"]
                if not model_data.empty:
                    sns.histplot(
                        model_data,
                        bins=bins,
                        ax=ax,
                        alpha=0.5,
                        color=palette[model],
                        label=model,
                        kde=True,
                        stat="count",
                    )

            ax.set_title(metric, fontsize=12, fontweight="bold")
            ax.set_xlabel("Score", fontsize=10)
            ax.set_ylabel("Frequency", fontsize=10)
            ax.legend(title="Model", fontsize=8)
            ax.grid(axis="y", alpha=0.3)

        # Hide unused axes
        for idx in range(len(available_metrics), len(axes)):
            axes[idx].axis("off")

        save_plot(output_dir, "metric_histograms.png")
