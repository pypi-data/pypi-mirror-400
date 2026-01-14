"""Script to download, process, and canonicalize MUV dataset with maxmin split generation.

This script:
1. Downloads the MUV dataset from HuggingFace
2. Processes each target with canonicalization
3. Removes invalid molecules
4. Generates train/test splits using maxmin method
5. Updates splits after removing invalid molecules
6. Saves processed parquet files and splits
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from rdkit import Chem
from tqdm import tqdm

from litmus.model_selection.splitters.maxmin_split import maxmin_train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def canonicalize_smiles(smiles: str) -> Optional[str]:
    """Return canonical SMILES or None if the input is invalid."""
    if pd.isna(smiles) or not isinstance(smiles, str) or not smiles.strip():
        return None

    try:
        mol = Chem.MolFromSmiles(smiles)
        return Chem.MolToSmiles(mol, canonical=True)

    except Exception:
        return None


def download_dataset(url: str, output_path: Path) -> None:
    """Download dataset from URL with progress bar."""
    logger.info(f"Downloading MUV dataset from {url}")
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    with (
        open(output_path, "wb") as f,
        tqdm(
            desc="Downloading MUV dataset",
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar,
    ):
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)
    logger.info(f"Downloaded to {output_path}")


def process_target_with_canonicalization(
    target: str,
    df: pd.DataFrame,
    output_path: Path,
) -> Tuple[pd.DataFrame, List[int], List[str]]:
    """Process a target with canonicalization and return dataframe with removed indices and original SMILES list.

    Returns
    -------
        Tuple of (dataframe, removed_indices, original_smiles_list)
    """
    logger.info(f"Processing target: {target}")

    # Filter out rows where target is NaN
    target_df = df[["SMILES", target]].dropna(subset=[target])

    if len(target_df) == 0:
        logger.warning(f"No data found for target {target}")
        return pd.DataFrame(columns=["SMILES", target]), [], []

    original_smiles_list = target_df["SMILES"].tolist()
    labels = target_df[target].tolist()

    # Canonicalize and filter
    logger.info(f"Canonicalizing {len(original_smiles_list)} SMILES for {target}")
    canonical_data = []
    removed_indices = []
    # Track mapping from original index to new index after removal
    original_to_new_idx = {}
    new_idx = 0

    for original_idx, (original_smiles, label) in enumerate(
        tqdm(
            zip(original_smiles_list, labels),
            desc=f"Canonicalizing {target}",
            total=len(original_smiles_list),
        )
    ):
        canonical = canonicalize_smiles(original_smiles)
        if canonical is None:
            removed_indices.append(original_idx)
        else:
            canonical_data.append({"SMILES": canonical, target: label})
            original_to_new_idx[original_idx] = new_idx
            new_idx += 1

    df_processed = pd.DataFrame(canonical_data)
    # Reset index to ensure 0-based consecutive indices
    df_processed = df_processed.reset_index(drop=True)

    logger.info(
        f"Target {target}: {len(original_smiles_list)} -> {len(df_processed)} molecules "
        f"({len(removed_indices)} removed)"
    )

    # Save processed dataset
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_parquet(output_path, index=False)
    logger.info(f"Saved processed dataset to {output_path}")

    return df_processed, removed_indices, original_smiles_list


def generate_splits_for_target(
    df: pd.DataFrame,
    target: str,
    removed_indices: List[int],
    random_state: int = 42,
    train_size: float = 0.75,
    show_progress: bool = False,
) -> Dict[str, np.ndarray]:
    """Generate train/test splits using maxmin method for a target.

    Parameters
    ----------
    df : pd.DataFrame
        Processed dataframe with canonicalized SMILES (with reset index 0..n-1)
    target : str
        Target name
    removed_indices : List[int]
        List of original indices that were removed during canonicalization
    random_state : int, default=42
        Random state for reproducibility
    train_size : float, default=0.75
        Proportion of data for training
    show_progress : bool, default=False
        Show progress bar during split generation

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary with 'train' and 'test' split indices (0-based indices in processed dataframe)
    """
    logger.info(f"Generating splits for {target} using maxmin method")

    # Get actives and inactives (df already has reset index from processing)
    active_df = df[df[target] == 1]
    inactive_df = df[df[target] == 0]

    active_smiles = active_df["SMILES"].tolist()
    inactive_smiles = inactive_df["SMILES"].tolist()

    logger.info(
        f"{target}: {len(active_smiles)} actives, {len(inactive_smiles)} inactives"
    )

    # Generate splits separately for actives and inactives
    train_active_idx, test_active_idx = maxmin_train_test_split(
        data=active_smiles,
        train_size=train_size,
        random_state=random_state,
        show_progress=show_progress,
    )

    train_inactive_idx, test_inactive_idx = maxmin_train_test_split(
        data=inactive_smiles,
        train_size=train_size,
        random_state=random_state,
        show_progress=show_progress,
    )

    # Map back to dataframe indices (0-based after reset)
    active_indices = active_df.index.tolist()
    inactive_indices = inactive_df.index.tolist()

    # Convert relative indices to absolute dataframe indices
    train_active_abs = [active_indices[i] for i in train_active_idx]
    test_active_abs = [active_indices[i] for i in test_active_idx]
    train_inactive_abs = [inactive_indices[i] for i in train_inactive_idx]
    test_inactive_abs = [inactive_indices[i] for i in test_inactive_idx]

    # Combine train and test indices
    train_idx = train_active_abs + train_inactive_abs
    test_idx = test_active_abs + test_inactive_abs

    # Convert to numpy arrays and sort
    train_idx = np.array(sorted(train_idx), dtype=int)
    test_idx = np.array(sorted(test_idx), dtype=int)

    # Calculate active ratios
    active_ratio_train = (
        len(train_active_idx) / len(train_idx) * 100 if len(train_idx) > 0 else 0
    )
    active_ratio_test = (
        len(test_active_idx) / len(test_idx) * 100 if len(test_idx) > 0 else 0
    )

    logger.info(
        f"{target} splits: train={len(train_idx)}, test={len(test_idx)} "
        f"(active ratio: train={active_ratio_train:.1f}%, test={active_ratio_test:.1f}%)"
    )

    return {"train": train_idx, "test": test_idx}


def save_splits(
    splits: Dict[str, np.ndarray], splits_dir: Path, target: str, dataset_prefix: str
) -> None:
    """Save split indices to files."""
    splits_dir.mkdir(parents=True, exist_ok=True)
    for split_name, indices in splits.items():
        split_path = splits_dir / f"{dataset_prefix}_{target}.{split_name}_idx.npy"
        np.save(split_path, indices)
        logger.info(f"Saved {split_name} split to {split_path}")


def process_muv_dataset(
    output_dir: Optional[Path] = None,
    splits_dir: Optional[Path] = None,
    cache_dir: Optional[Path] = None,
    force_download: bool = False,
    random_state: int = 42,
    train_size: float = 0.75,
) -> None:
    """Main function to download, process, and canonicalize MUV dataset.

    Parameters
    ----------
    output_dir : Optional[Path], default=None
        Directory to save processed datasets. If None, uses cache_dir.
    splits_dir : Optional[Path], default=None
        Directory to save splits. If None, uses output_dir / "splits".
    cache_dir : Optional[Path], default=None
        Directory for temporary files (downloads). If None, uses sklearn cache.
    force_download : bool, default=False
        Force re-download.
    random_state : int, default=42
        Random state for split generation.
    train_size : float, default=0.75
        Proportion of data for training.
    """
    # Setup paths
    if cache_dir is None:
        from sklearn.datasets import get_data_home

        cache_dir = Path(get_data_home()) / "litmus" / "datasets"
    else:
        cache_dir = Path(cache_dir)

    if output_dir is None:
        output_dir = cache_dir
    else:
        output_dir = Path(output_dir)

    if splits_dir is None:
        splits_dir = output_dir / "splits"
    else:
        splits_dir = Path(splits_dir)

    cache_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    splits_dir.mkdir(parents=True, exist_ok=True)

    # Dataset URL and metadata
    dataset_url = "https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_MUV/resolve/main/muv.csv"
    csv_path = cache_dir / "muv.csv"
    dataset_prefix = "muv"

    # Available targets
    available_targets = [
        "MUV-466",
        "MUV-548",
        "MUV-600",
        "MUV-644",
        "MUV-652",
        "MUV-689",
        "MUV-692",
        "MUV-712",
        "MUV-713",
        "MUV-733",
        "MUV-737",
        "MUV-810",
        "MUV-832",
        "MUV-846",
        "MUV-852",
        "MUV-858",
        "MUV-859",
    ]

    # Download if needed
    if not csv_path.exists() or force_download:
        download_dataset(dataset_url, csv_path)
    else:
        logger.info(f"Using existing download: {csv_path}")

    # Load the full dataset
    logger.info("Loading MUV dataset...")
    df_full = pd.read_csv(csv_path)
    logger.info(
        f"Loaded dataset with {len(df_full)} rows and {len(df_full.columns)} columns"
    )
    logger.info(f"Columns: {list(df_full.columns)}")

    # Process each target
    logger.info(f"Found {len(available_targets)} targets: {available_targets}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Splits directory: {splits_dir}")

    for target in tqdm(available_targets, desc="Processing targets"):
        output_path = output_dir / f"{dataset_prefix}_{target}.parquet"

        # Process target with canonicalization
        (
            df_processed,
            removed_indices,
            original_smiles_list,
        ) = process_target_with_canonicalization(target, df_full, output_path)

        if len(df_processed) == 0:
            logger.warning(
                f"Skipping split generation for {target} (no valid molecules)"
            )
            continue

        # Generate splits using maxmin method
        splits = generate_splits_for_target(
            df_processed,
            target,
            removed_indices,
            random_state=random_state,
            train_size=train_size,
            show_progress=False,
        )

        # Save splits
        save_splits(splits, splits_dir, target, dataset_prefix)

    # Summary
    logger.info("=" * 60)
    logger.info("Processing completed!")
    logger.info(f"Processed datasets saved to: {output_dir}")
    logger.info(f"  - Format: {dataset_prefix}_<target>.parquet")
    logger.info(f"Splits saved to: {splits_dir}")
    logger.info(f"  - Format: {dataset_prefix}_<target>.train_idx.npy")
    logger.info(f"  - Format: {dataset_prefix}_<target>.test_idx.npy")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download, process, and canonicalize MUV dataset with maxmin split generation"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save processed datasets (default: cache_dir)",
    )
    parser.add_argument(
        "--splits-dir",
        type=Path,
        help="Directory to save splits (default: output_dir / 'splits')",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        help="Directory for temporary files (default: sklearn cache)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random state for split generation (default: 42)",
    )
    parser.add_argument(
        "--train-size",
        type=float,
        default=0.75,
        help="Proportion of data for training (default: 0.75)",
    )

    args = parser.parse_args()
    process_muv_dataset(
        output_dir=args.output_dir,
        splits_dir=args.splits_dir,
        cache_dir=args.cache_dir,
        force_download=args.force,
        random_state=args.random_state,
        train_size=args.train_size,
    )
