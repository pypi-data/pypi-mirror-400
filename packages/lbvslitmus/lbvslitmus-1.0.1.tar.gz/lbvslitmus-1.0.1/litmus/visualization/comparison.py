"""
Model comparison plots.
"""


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .constants import COMPARISON_METRICS, PERFORMANCE_METRICS
from .utils import (
    get_metric_subset,
    get_model_palette,
    load_results,
    plotting_context,
    save_plot,
)


def plot_model_comparison(
    results,
    output_dir: str = "plots",
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Compare models for main metrics using boxplots.

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
            df=df,
            metrics=COMPARISON_METRICS,
            empty_message="No data for model comparison",
        )

        # None if DataFrame is empty or doesn't contain any of the required metrics
        if df_filtered is None:
            return

        models = sorted(df_filtered["model"].unique())
        palette = get_model_palette(models)

        n_metrics = len(COMPARISON_METRICS)
        n_cols = min(n_metrics, 2)
        n_rows = (n_metrics + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(7 * n_cols, 5 * n_rows))
        axes = np.atleast_1d(axes).flatten()

        for idx, metric in enumerate(COMPARISON_METRICS):
            ax = axes[idx]
            metric_data = df_filtered[df_filtered["metric"] == metric]

            if metric_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    f"No data for {metric}",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(metric)
                continue

            sns.boxplot(
                data=metric_data,
                x="model",
                y="score",
                hue="model",
                ax=ax,
                palette=palette,
                legend=False,
            )
            ax.set_title(f"{metric} - Model Comparison", fontsize=12, fontweight="bold")
            ax.set_xlabel("Model", fontsize=10)
            ax.set_ylabel("Score", fontsize=10)
            ax.tick_params(axis="x", rotation=45)

            # Get x-tick labels to ensure correct model-position mapping
            tick_labels = [t.get_text() for t in ax.get_xticklabels()]
            box_positions = ax.get_xticks()

            for i, model_name in enumerate(tick_labels):
                if model_name and i < len(box_positions):
                    model_scores = metric_data.loc[
                        metric_data["model"] == model_name, "score"
                    ]
                    if not model_scores.empty:
                        mean_val = model_scores.mean()
                        ax.text(
                            box_positions[i],
                            mean_val,
                            f"{mean_val:.3f}",
                            ha="center",
                            va="bottom",
                            fontweight="bold",
                        )

        # Hide unused axes if grid has more subplots than metrics
        for idx in range(n_metrics, len(axes)):
            axes[idx].axis("off")

        save_plot(output_dir, "model_comparison.png")


def plot_benchmark_performance(
    results,
    output_dir: str = "plots",
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
) -> None:
    """
    Model performance across different benchmarks.

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
            df, PERFORMANCE_METRICS, "No data for benchmark performance plot"
        )

        if df_filtered is None:
            return

        models = sorted(df_filtered["model"].unique())
        palette = get_model_palette(models)

        fig, axes = plt.subplots(
            1,
            len(PERFORMANCE_METRICS),
            figsize=(8 * len(PERFORMANCE_METRICS), 6),
        )
        axes = np.atleast_1d(axes).flatten()

        for idx, metric in enumerate(PERFORMANCE_METRICS):
            ax = axes[idx]
            metric_data = df_filtered[df_filtered["metric"] == metric]

            if metric_data.empty:
                continue

            summary = (
                metric_data.groupby(["benchmark", "model"])["score"]
                .mean()
                .reset_index()
            )
            pivot_data = summary.pivot(
                index="benchmark", columns="model", values="score"
            )

            # Reorder columns to match models order for consistent colors
            available_models = [m for m in models if m in pivot_data.columns]
            if not available_models:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"{metric} - Average Performance Across Benchmarks")
                continue

            pivot_data = pivot_data[available_models]
            model_colors = [palette[m] for m in available_models]
            pivot_data.plot(kind="bar", ax=ax, width=0.8, color=model_colors)
            ax.set_title(
                f"{metric} - Average Performance Across Benchmarks",
                fontsize=12,
                fontweight="bold",
            )
            ax.set_xlabel("Benchmark", fontsize=10)
            ax.set_ylabel("Average Score", fontsize=10)
            ax.legend(title="Model", fontsize=9)
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", alpha=0.3)

        save_plot(output_dir, "benchmark_performance.png")
