"""
Bar plots for metrics and targets.
"""

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .constants import COMPARISON_METRICS, ENRICHMENT_METRICS, METRIC_PALETTE
from .utils import (
    get_metric_subset,
    get_model_palette,
    load_results,
    plotting_context,
    save_plot,
)


def plot_metric_bars(
    results,
    output_dir: str = "plots",
    metrics: Optional[Sequence[str]] = None,
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create grouped bar plots showing metric scores across datasets.

    Generates subplots for each benchmark with grouped bars for different metrics
    and models.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    metrics : Sequence[str], optional
        List of metrics to plot. Defaults to COMPARISON_METRICS
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
        metrics_to_plot = metrics if metrics is not None else COMPARISON_METRICS
        df_filtered = get_metric_subset(df, metrics_to_plot, "No data for metric bars")

        if df_filtered is None:
            return

        benchmarks = sorted(df_filtered["benchmark"].unique())
        models = sorted(df_filtered["model"].unique())
        palette = get_model_palette(models)
        n_benchmarks = len(benchmarks)

        fig, axes = plt.subplots(1, n_benchmarks, figsize=(5 * n_benchmarks, 6))
        axes = np.atleast_1d(axes).flatten()

        for idx, benchmark in enumerate(benchmarks):
            ax = axes[idx]
            bench_data = df_filtered[df_filtered["benchmark"] == benchmark]

            if bench_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(benchmark)
                continue

            summary = (
                bench_data.groupby(["metric", "model"])["score"].mean().reset_index()
            )

            sns.barplot(
                data=summary,
                x="metric",
                y="score",
                hue="model",
                ax=ax,
                palette=palette,
            )

            ax.set_title(benchmark, fontsize=12, fontweight="bold")
            ax.set_xlabel("Metric", fontsize=10)
            ax.set_ylabel("Average Score", fontsize=10)
            ax.tick_params(axis="x", rotation=45)
            ax.legend(title="Model", fontsize=8)
            ax.grid(axis="y", alpha=0.3)

        save_plot(output_dir, "metric_bars.png")


def plot_enrichment_factors(
    results,
    output_dir: str = "plots",
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create a bar plot showing Enrichment Factor values for different datasets.

    Displays EF 1% and EF 5% values for each benchmark and model combination.

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
            df, ENRICHMENT_METRICS, "No enrichment factor data found"
        )

        if df_filtered is None:
            return

        summary = (
            df_filtered.groupby(["benchmark", "model", "metric"])["score"]
            .mean()
            .reset_index()
        )

        # Create combination of benchmark and model for x-axis
        summary["benchmark_model"] = summary["benchmark"] + "\n" + summary["model"]

        fig, ax = plt.subplots(figsize=(14, 7))

        pivot_data = summary.pivot(
            index="benchmark_model", columns="metric", values="score"
        )
        pivot_data = pivot_data.reindex(
            columns=[m for m in ENRICHMENT_METRICS if m in pivot_data.columns]
        )

        # Use dedicated metric palette for enrichment metrics
        metric_colors = METRIC_PALETTE[: len(pivot_data.columns)]

        if pivot_data.empty:
            ax.text(
                0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes
            )
        else:
            pivot_data.plot(kind="bar", ax=ax, width=0.8, color=metric_colors)

            ax.set_xlabel("Benchmark", fontsize=11)
            ax.set_ylabel("Enrichment Factor", fontsize=11)
            ax.set_title(
                "Enrichment Factors - Model Comparison", fontsize=14, fontweight="bold"
            )
            ax.legend(title="Metric", loc="upper right")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", alpha=0.3)

        save_plot(output_dir, "enrichment_factors.png")


def plot_top_targets(
    results,
    output_dir: str = "plots",
    metrics: Optional[Sequence[str]] = None,
    n_targets: int = 15,
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Create horizontal bar plots showing top N targets for each metric.

    Displays the best performing targets with bars for each model.
    Target labels include the dataset name in parentheses.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results
    output_dir : str, default="plots"
        Directory to save the plot
    metrics : Sequence[str], optional
        List of metrics to plot. Defaults to ["AUROC", "AUPRC"]
    n_targets : int, default=15
        Number of top targets to display
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
        default_metrics = ["AUROC", "AUPRC"]
        metrics_to_plot = metrics if metrics is not None else default_metrics
        df_filtered = get_metric_subset(df, metrics_to_plot, "No data for top targets")

        if df_filtered is None:
            return

        available_metrics = [
            m for m in metrics_to_plot if m in df_filtered["metric"].unique()
        ]
        models = sorted(df_filtered["model"].unique())
        n_metrics = len(available_metrics)

        # Create model palette
        palette = get_model_palette(models)

        fig, axes = plt.subplots(
            1, n_metrics, figsize=(8 * n_metrics, max(8, n_targets * 0.5))
        )
        axes = np.atleast_1d(axes).flatten()

        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            metric_data = df_filtered[df_filtered["metric"] == metric].copy()

            if metric_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"{metric} - Top {n_targets} Targets")
                continue

            # Create target label with dataset name
            metric_data["target_label"] = (
                metric_data["target"] + " (" + metric_data["benchmark"] + ")"
            )

            # Get average score per target_label across all models
            target_avg = (
                metric_data.groupby("target_label")["score"]
                .mean()
                .sort_values(ascending=False)
            )
            top_target_labels = target_avg.head(n_targets).index.tolist()

            # Filter to top targets and create summary
            top_data = metric_data[metric_data["target_label"].isin(top_target_labels)]
            summary = (
                top_data.groupby(["target_label", "model"])["score"]
                .mean()
                .reset_index()
            )

            # Pivot for plotting
            pivot_data = summary.pivot(
                index="target_label", columns="model", values="score"
            )
            pivot_data = pivot_data.reindex(top_target_labels)

            # Plot horizontal bars
            y_positions = np.arange(len(top_target_labels))
            bar_height = 0.8 / len(models)

            for model_idx, model in enumerate(models):
                if model in pivot_data.columns:
                    offset = (model_idx - len(models) / 2 + 0.5) * bar_height
                    ax.barh(
                        y_positions + offset,
                        pivot_data[model],
                        bar_height,
                        label=model,
                        color=palette[model],
                    )

            ax.set_yticks(y_positions)
            ax.set_yticklabels(top_target_labels)
            ax.invert_yaxis()
            ax.set_xlabel("Score", fontsize=10)
            ax.set_ylabel("Target", fontsize=10)
            ax.set_title(
                f"{metric} - Top {n_targets} Targets", fontsize=12, fontweight="bold"
            )
            ax.legend(title="Model", loc="lower right", fontsize=8)
            ax.grid(axis="x", alpha=0.3)

        save_plot(output_dir, "top_targets.png")
