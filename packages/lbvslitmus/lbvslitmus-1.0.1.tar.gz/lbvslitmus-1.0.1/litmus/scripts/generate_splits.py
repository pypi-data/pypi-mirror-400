"""
Script to generate train/test splits for all registered datasets in Litmus.

This script will:
1. List all available datasets from the registry
2. For each dataset, generate splits for all available targets
3. Save the splits using the existing generate_split method
"""

import argparse
import logging
import multiprocessing
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional

import numpy as np
from tqdm import tqdm

from litmus.datasets.downloader import DatasetDownloader
from litmus.datasets.lit_pcba import LITPCBADownloader
from litmus.datasets.muv import MUVDownloader
from litmus.datasets.registry import registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Thread-local storage for logging
thread_local = threading.local()


def register_datasets() -> None:
    """Register all available dataset downloaders."""
    registry.register(MUVDownloader)
    registry.register(LITPCBADownloader)


def get_all_targets(downloader: DatasetDownloader) -> List[str]:
    """Get all available targets for a dataset."""
    # Get targets from metadata
    return downloader.metadata.available_targets


def check_split_exists(downloader: DatasetDownloader, target: str) -> bool:
    """
    Check if split already exists for a given target.

    Parameters
    ----------
    downloader : DatasetDownloader
        Dataset downloader instance
    target : str
        Target name to check

    Returns
    -------
    bool
        True if split exists, False otherwise
    """
    try:
        # Create splits directory if it doesn't exist
        splits_dir = downloader.cache_dir / "splits"
        splits_dir.mkdir(exist_ok=True)

        # Get base filename without extension
        base_path = downloader.get_dataset_path(target)
        base_name = base_path.stem

        # Check if both train and test index files exist in splits directory
        train_idx_path = splits_dir / f"{base_name}.train_idx.npy"
        test_idx_path = splits_dir / f"{base_name}.test_idx.npy"

        return train_idx_path.exists() and test_idx_path.exists()
    except (ValueError, FileNotFoundError):
        return False


def process_target(dataset_name: str, target: str, force: bool = False) -> None:
    """
    Process a single target for a dataset.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset
    target : str
        Name of the target to process
    force : bool, default=False
        If True, regenerate split even if it exists
    """
    try:
        # Register datasets in the worker process
        register_datasets()

        downloader = registry.get_downloader(dataset_name)

        # Create splits directory if it doesn't exist
        splits_dir = downloader.cache_dir / "splits"
        splits_dir.mkdir(exist_ok=True)

        # Get base filename without extension
        base_path = downloader.get_dataset_path(target)
        base_name = base_path.stem

        # Define split file paths
        train_idx_path = splits_dir / f"{base_name}.train_idx.npy"
        test_idx_path = splits_dir / f"{base_name}.test_idx.npy"

        # Check if split already exists
        if not force and train_idx_path.exists() and test_idx_path.exists():
            return

        # Load the dataset for this specific target
        df = downloader.load(target)

        # Generate splits
        train_idx, test_idx = downloader.generate_split(target, show_progress=False)

        # Save the splits to the splits directory
        np.save(train_idx_path, train_idx)
        np.save(test_idx_path, test_idx)

        # Calculate active ratios
        active_ratio_train = np.mean([df[target].iloc[i] == 1 for i in train_idx])
        active_ratio_test = np.mean([df[target].iloc[i] == 1 for i in test_idx])

        logger.info(
            "[%s] %s: Generated split (train: %d, test: %d, active ratio: %.1f%%/%.1f%%)",
            dataset_name,
            target,
            len(train_idx),
            len(test_idx),
            active_ratio_train * 100,
            active_ratio_test * 100,
        )
    except Exception:
        logger.exception("[%s] %s: Error processing target", dataset_name, target)


def generate_splits_for_dataset(
    dataset_name: str, max_workers: Optional[int] = None, force: bool = False
) -> None:
    """
    Generate splits for all targets in a dataset using multiple processes.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset to process
    max_workers : Optional[int], default=None
        Maximum number of worker processes (defaults to CPU count)
    force : bool, default=False
        If True, regenerate splits even if they exist
    """
    try:
        # Register datasets in the main process
        register_datasets()

        downloader = registry.get_downloader(dataset_name)

        # Get all available targets
        targets = get_all_targets(downloader)
        logger.info("Processing %s (%d targets)", dataset_name, len(targets))

        if max_workers is None:
            max_workers = multiprocessing.cpu_count()

        # Process targets in parallel using processes
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_target = {
                executor.submit(process_target, dataset_name, target, force): target
                for target in targets
            }

            # Process completed tasks with progress bar
            for future in tqdm(
                as_completed(future_to_target),
                total=len(targets),
                desc=f"Processing {dataset_name}",
                unit="target",
                position=0,
                leave=True,
            ):
                target = future_to_target[future]
                try:
                    future.result()
                except Exception:
                    logger.exception("Error processing target %s", target)

    except Exception:
        logger.exception("Error processing dataset %s", dataset_name)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate train/test splits for datasets"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of splits even if they already exist",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Specific dataset to process (e.g., 'MUV', 'LIT-PCBA')",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        help="Maximum number of worker processes",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (optional)",
    )
    return parser.parse_args()


def setup_logging(log_file: Optional[str] = None) -> None:
    """Set up logging configuration.

    Parameters
    ----------
    log_file : Optional[str], default=None
        Log file path (optional)
    """
    if log_file:
        # Add file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)


def main() -> None:
    """Generate splits for all datasets."""
    args = parse_args()

    # Setup logging
    setup_logging(args.log_file)

    # Register datasets
    register_datasets()

    # Get available datasets
    available_datasets = list(registry.list_datasets().keys())
    logger.info("Available datasets: %s", available_datasets)

    if args.dataset:
        if args.dataset not in available_datasets:
            logger.error(
                "Dataset '%s' not found. Available: %s",
                args.dataset,
                available_datasets,
            )
            return
        datasets_to_process = [args.dataset]
    else:
        datasets_to_process = available_datasets

    # Process each dataset
    for dataset_name in datasets_to_process:
        logger.info("Starting processing of dataset: %s", dataset_name)
        generate_splits_for_dataset(
            dataset_name, max_workers=args.max_workers, force=args.force
        )
        logger.info("Completed processing of dataset: %s", dataset_name)

    logger.info("All datasets processed successfully!")


if __name__ == "__main__":
    main()
