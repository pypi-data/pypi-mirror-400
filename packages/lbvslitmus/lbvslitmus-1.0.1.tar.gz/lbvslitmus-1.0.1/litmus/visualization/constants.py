"""
Constants for visualization module.
"""

# Metric constants
COMPARISON_METRICS = ["AUROC", "AUPRC", "BEDROC"]
PERFORMANCE_METRICS = ["AUROC", "AUPRC"]
HEATMAP_METRICS = [
    "AUROC",
    "AUPRC",
    "BEDROC",
    "accuracy",
    "F1 score",
    "MCC",
]
BOUNDED_METRICS = ["AUROC", "AUPRC", "BEDROC", "accuracy", "F1 score", "MCC"]
VIOLIN_GRID_METRICS = ["AUROC", "AUPRC", "BEDROC"]
DISTRIBUTION_METRICS = ["AUROC", "AUPRC", "BEDROC"]
HISTOGRAM_METRICS = ["AUROC", "AUPRC", "BEDROC", "accuracy", "F1 score", "MCC"]
ENRICHMENT_METRICS = ["Enrichment factor 1%", "Enrichment factor 5%"]
CORRELATION_METRICS = ["AUPRC", "AUROC", "BEDROC", "MCC", "accuracy", "F1 score"]

# Default color palette for models
MODEL_PALETTE = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"]

# Color palette for metrics (used in enrichment factors, etc.)
METRIC_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
