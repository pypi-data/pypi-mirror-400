"""
Utility functions for visualization module.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .constants import BOUNDED_METRICS, MODEL_PALETTE


def get_model_palette(models: Sequence[str]) -> dict[str, str]:
    """
    Create a consistent color palette for models.

    Parameters
    ----------
    models : Sequence[str]
        List of model names

    Returns
    -------
    dict[str, str]
        Dictionary mapping model names to colors
    """
    return {
        model: MODEL_PALETTE[i % len(MODEL_PALETTE)] for i, model in enumerate(models)
    }


def load_results(results) -> pd.DataFrame:
    """
    Load benchmark results into a DataFrame.

    Parameters
    ----------
    results : BenchmarkResults or pd.DataFrame or str
        Benchmark results. Can be:
        - BenchmarkResults object
        - pandas DataFrame
        - Path to CSV file

    Returns
    -------
    pd.DataFrame
        Processed DataFrame with benchmark results

    Raises
    ------
    TypeError
        If results is not a supported type
    ValueError
        If required columns are missing
    """
    if isinstance(results, (Path, str)):
        df = pd.read_csv(results)

    elif hasattr(results, "to_dataframe"):
        df = results.to_dataframe()

    elif isinstance(results, pd.DataFrame):
        df = results.copy()

    else:
        raise TypeError(
            "results must be BenchmarkResults, pd.DataFrame, or path to CSV file"
        )

    # Validate required columns
    required_columns = {"benchmark", "model", "target", "metric", "score"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if "seed" not in df.columns:
        df["seed"] = np.nan

    df["seed"] = pd.to_numeric(df["seed"], errors="coerce")
    df = _filter_welqrate_averaged_results(df)

    return df


def get_metric_subset(
    df: pd.DataFrame, metrics: Sequence[str], empty_message: str
) -> Optional[pd.DataFrame]:
    """
    Filter DataFrame to only include specified metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    metrics : Sequence[str]
        List of metrics to include
    empty_message : str
        Message to print if no data found

    Returns
    -------
    Optional[pd.DataFrame]
        Filtered DataFrame or None if empty
    """
    if df.empty or "metric" not in df.columns:
        print(empty_message)
        return None

    df_filtered = df[df["metric"].isin(metrics)].copy()

    if df_filtered.empty:
        print(empty_message)
        return None

    return df_filtered


def heatmap_bounds(
    pivot_data: pd.DataFrame, metrics: Sequence[str]
) -> tuple[float, float]:
    """
    Calculate appropriate bounds for heatmap colorbar.

    Parameters
    ----------
    pivot_data : pd.DataFrame
        Pivot table with metric values
    metrics : Sequence[str]
        List of metrics being displayed

    Returns
    -------
    tuple[float, float]
        (vmin, vmax) bounds for the heatmap
    """
    if not metrics:
        return 0, 1

    if all(metric in BOUNDED_METRICS for metric in metrics):
        return 0, 1

    if pivot_data.empty or pivot_data.isna().all().all():
        return 0, 1

    data_min = pivot_data.min().min()
    data_max = pivot_data.max().max()

    if pd.isna(data_min) or pd.isna(data_max):
        return 0, 1

    return max(0, data_min * 0.95), data_max * 1.05


def _filter_welqrate_averaged_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep WELQRATE averaged rows (no seed) and everything else.

    For WELQRATE benchmark, we only want averaged results (rows without seed),
    not individual seed runs.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame
    """
    if df.empty or "benchmark" not in df.columns:
        return df.copy()

    welqrate_with_seed = (df["benchmark"] == "WELQRATE") & (df["seed"].notna())

    return df[~welqrate_with_seed].copy()


def save_plot(output_dir: str, filename: str) -> None:
    """
    Save the current matplotlib figure to a file.

    Parameters
    ----------
    output_dir : str
        Directory to save the plot
    filename : str
        Name of the output file
    """
    plt.tight_layout()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    plt.savefig(output_path / filename, bbox_inches="tight")
    print(f"Saved: {output_path / filename}")
    plt.close()


@contextmanager
def plotting_context(
    style: str = "whitegrid",
    figure_dpi: int = 100,
    savefig_dpi: int = 300,
    font_size: int = 10,
):
    """
    Context manager for matplotlib/seaborn plot settings.

    Ensures settings are applied only within the context and restored afterward.
    """
    original_backend = matplotlib.get_backend()
    original_rcparams = plt.rcParams.copy()

    try:
        matplotlib.use("Agg")
        sns.set_style(style)
        plt.rcParams["figure.dpi"] = figure_dpi
        plt.rcParams["savefig.dpi"] = savefig_dpi
        plt.rcParams["font.size"] = font_size
        yield

    finally:
        plt.rcParams.update(original_rcparams)
        try:
            matplotlib.use(original_backend)
        except Exception:
            pass  # Backend switching may not always be possible
