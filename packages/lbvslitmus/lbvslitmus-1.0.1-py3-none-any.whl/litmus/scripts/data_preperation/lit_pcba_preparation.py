"""Script to download, process, and canonicalize LIT-PCBA dataset from AVE_unbiased.tgz.

This script:
1. Downloads the dataset from http://drugdesign.unistra.fr/LIT-PCBA/Files/AVE_unbiased.tgz
2. Processes each target with canonicalization
3. Removes invalid molecules and updates splits accordingly
4. Saves processed parquet files
"""

import logging
import shutil
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from rdkit import Chem
from tqdm import tqdm

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
    logger.info(f"Downloading dataset from {url}")
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    with (
        open(output_path, "wb") as f,
        tqdm(
            desc="Downloading LIT-PCBA dataset",
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


def extract_dataset(tar_path: Path, extract_dir: Path) -> None:
    """Extract tar.gz archive."""
    logger.info(f"Extracting {tar_path} to {extract_dir}")
    extract_dir.mkdir(exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tqdm(tar, desc="Extracting archive"):
            tar.extract(member, extract_dir)
    logger.info(f"Extracted to {extract_dir}")


def explore_dataset_structure(extract_dir: Path) -> Dict:
    """Explore the structure of the extracted dataset."""
    logger.info("Exploring dataset structure...")
    structure = {
        "root_files": [],
        "directories": [],
        "targets": {},
    }

    # List root level
    for item in extract_dir.iterdir():
        if item.is_file():
            structure["root_files"].append(item.name)
        elif item.is_dir():
            structure["directories"].append(item.name)

    logger.info(f"Root files: {structure['root_files']}")
    logger.info(f"Directories: {structure['directories']}")

    # Explore each directory (targets)
    for dir_name in structure["directories"]:
        target_dir = extract_dir / dir_name
        target_info = {
            "files": [],
            "has_actives": False,
            "has_inactives": False,
        }

        for item in target_dir.iterdir():
            if item.is_file():
                target_info["files"].append(item.name)
                if "active" in item.name.lower():
                    target_info["has_actives"] = True
                if "inactive" in item.name.lower():
                    target_info["has_inactives"] = True

        structure["targets"][dir_name] = target_info
        logger.info(f"Target {dir_name}: {target_info}")

    return structure


def load_smiles_file(file_path: Path) -> List[str]:
    """Load SMILES from a file (handles .smi format)."""
    smiles_list = []
    if not file_path.exists():
        return smiles_list

    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # SMILES files typically have SMILES as first column
            smiles = line.split()[0]
            smiles_list.append(smiles)

    return smiles_list


def process_target_with_canonicalization(
    target: str,
    target_dir: Path,
    output_path: Path,
) -> Tuple[pd.DataFrame, List[int], List[str], Dict[str, np.ndarray]]:
    """Process a target with canonicalization and return dataframe with removed indices and original SMILES list.

    Returns
    -------
        Tuple of (dataframe, removed_indices, original_smiles_list, split_indices_dict)
        split_indices_dict contains 'train' and 'test' lists of original indices before canonicalization
    """
    logger.info(f"Processing target: {target}")

    smiles_dict = {}
    original_indices = {}  # Map from original SMILES to original index
    original_smiles_list = []  # List to preserve order
    split_indices_dict = {
        "train": [],
        "test": [],
    }  # Track which indices are in train/test

    # Load actives/inactive - AVE_unbiased format (active_T.smi, active_V.smi, inactive_T.smi, inactive_V.smi)
    active_T_file = target_dir / "active_T.smi"
    active_V_file = target_dir / "active_V.smi"
    inactive_T_file = target_dir / "inactive_T.smi"
    inactive_V_file = target_dir / "inactive_V.smi"

    if (
        not active_T_file.exists()
        or not active_V_file.exists()
        or not inactive_T_file.exists()
        or not inactive_V_file.exists()
    ):
        logger.warning(f"No data found for target {target}")
        return (
            pd.DataFrame(columns=["SMILES", target]),
            [],
            [],
            {"train": np.array([], dtype=int), "test": np.array([], dtype=int)},
        )

    # AVE_unbiased format: T = train, V = test/validation
    active_T_smiles = load_smiles_file(active_T_file)
    active_V_smiles = load_smiles_file(active_V_file)

    # Add train actives
    for smiles in active_T_smiles:
        original_indices[smiles] = len(smiles_dict)
        original_smiles_list.append(smiles)
        smiles_dict[smiles] = 1
        split_indices_dict["train"].append(len(smiles_dict) - 1)

    # Add test actives
    for smiles in active_V_smiles:
        original_indices[smiles] = len(smiles_dict)
        original_smiles_list.append(smiles)
        smiles_dict[smiles] = 1
        split_indices_dict["test"].append(len(smiles_dict) - 1)

    inactive_T_smiles = load_smiles_file(inactive_T_file)
    inactive_V_smiles = load_smiles_file(inactive_V_file)

    # Add train inactives
    for smiles in inactive_T_smiles:
        original_indices[smiles] = len(smiles_dict)
        original_smiles_list.append(smiles)
        smiles_dict[smiles] = 0
        split_indices_dict["train"].append(len(smiles_dict) - 1)

    # Add test inactives
    for smiles in inactive_V_smiles:
        original_indices[smiles] = len(smiles_dict)
        original_smiles_list.append(smiles)
        smiles_dict[smiles] = 0
        split_indices_dict["test"].append(len(smiles_dict) - 1)

    if not smiles_dict:
        logger.warning(f"No data found for target {target}")
        return (
            pd.DataFrame(columns=["SMILES", target]),
            [],
            [],
            {"train": np.array([], dtype=int), "test": np.array([], dtype=int)},
        )

    # Canonicalize and filter
    logger.info(f"Canonicalizing {len(smiles_dict)} SMILES for {target}")
    canonical_data = []
    removed_indices = []
    # Track mapping from original index to new index after removal
    original_to_new_idx = {}
    new_idx = 0

    for original_idx, (original_smiles, label) in enumerate(smiles_dict.items()):
        canonical = canonicalize_smiles(original_smiles)
        if canonical is None:
            removed_indices.append(original_idx)
        else:
            canonical_data.append({"SMILES": canonical, target: label})
            original_to_new_idx[original_idx] = new_idx
            new_idx += 1

    df = pd.DataFrame(canonical_data)
    logger.info(
        f"Target {target}: {len(smiles_dict)} -> {len(df)} molecules "
        f"({len(removed_indices)} removed)"
    )

    # Update split indices to new indices after removal
    updated_split_indices = {}
    for split_name, original_split_indices in split_indices_dict.items():
        updated_indices = []
        for orig_idx in original_split_indices:
            if orig_idx in original_to_new_idx:
                updated_indices.append(original_to_new_idx[orig_idx])
        updated_split_indices[split_name] = np.array(updated_indices, dtype=int)
        logger.info(
            f"{split_name} split: {len(original_split_indices)} -> {len(updated_indices)} after canonicalization"
        )

    # Save processed dataset
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved processed dataset to {output_path}")

    return df, removed_indices, original_smiles_list, updated_split_indices


def save_splits(
    splits: Dict[str, np.ndarray], splits_dir: Path, target: str, dataset_prefix: str
) -> None:
    """Save split indices to files."""
    splits_dir.mkdir(parents=True, exist_ok=True)
    for split_name, indices in splits.items():
        split_path = splits_dir / f"{dataset_prefix}_{target}.{split_name}_idx.npy"
        np.save(split_path, indices)
        logger.info(f"Saved {split_name} split to {split_path}")


def main(
    output_dir: Optional[Path] = None,
    splits_dir: Optional[Path] = None,
    cache_dir: Optional[Path] = None,
    force_download: bool = False,
) -> None:
    """Main function to download, process, and canonicalize LIT-PCBA dataset.

    Parameters
    ----------
    output_dir : Optional[Path], default=None
        Directory to save processed datasets. If None, uses cache_dir.
    splits_dir : Optional[Path], default=None
        Directory to save splits. If None, uses output_dir / "splits".
    cache_dir : Optional[Path], default=None
        Directory for temporary files (downloads, extraction). If None, uses sklearn cache.
    force_download : bool, default=False
        Force re-download and re-extraction.
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

    # Dataset URL
    dataset_url = "http://drugdesign.unistra.fr/LIT-PCBA/Files/AVE_unbiased.tgz"
    tar_path = cache_dir / "AVE_unbiased.tgz"
    extract_dir = cache_dir / "lit_pcba_extracted"
    dataset_prefix = "LIT-PCBA"

    # Download if needed
    if not tar_path.exists() or force_download:
        download_dataset(dataset_url, tar_path)
    else:
        logger.info(f"Using existing download: {tar_path}")

    # Extract if needed
    if not extract_dir.exists() or force_download:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dataset(tar_path, extract_dir)
    else:
        logger.info(f"Using existing extraction: {extract_dir}")

    # Explore structure
    structure = explore_dataset_structure(extract_dir)

    # Process each target
    targets = list(structure["targets"].keys())
    if not targets:
        # Try to find targets in subdirectories
        for item in extract_dir.iterdir():
            if item.is_dir():
                targets.append(item.name)

    logger.info(f"Found {len(targets)} targets: {targets}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Splits directory: {splits_dir}")

    for target in tqdm(targets, desc="Processing targets"):
        target_dir = extract_dir / target
        if not target_dir.exists() or not target_dir.is_dir():
            logger.warning(f"Target directory {target_dir} does not exist, skipping")
            continue

        output_path = output_dir / f"{dataset_prefix}_{target}.parquet"

        # Process target with canonicalization
        (
            df,
            removed_indices,
            original_smiles_list,
            split_indices,
        ) = process_target_with_canonicalization(target, target_dir, output_path)

        logger.info(f"Using splits from AVE_unbiased format for {target}")
        save_splits(split_indices, splits_dir, target, dataset_prefix)

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
        description="Download, process, and canonicalize LIT-PCBA dataset"
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
        help="Force re-download and re-extraction",
    )

    args = parser.parse_args()
    main(
        output_dir=args.output_dir,
        splits_dir=args.splits_dir,
        cache_dir=args.cache_dir,
        force_download=args.force,
    )
