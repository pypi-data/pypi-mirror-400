"""Process WelQrate datasets and emit canonical scaffold splits.

Features:
- Reads WelQrate from a user-provided path (ZIP file or extracted directory)
- Canonicalizes SMILES for every supported target in ``standard_formats/``
- Loads scaffold splits (2d/3d, seeds 1..5) from ``split/scaffold/*.pt``
- Saves per-target Parquet files and seed-specific train/test indices (.npy)

Usage example:
python -m litmus.scripts.data_preperation.welqrate_preparation --zip-path F:\\WelQrate\\WelQrate.zip --scaffold 3d
"""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import torch
from rdkit import Chem
from sklearn.datasets import get_data_home
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AVAILABLE_TARGETS = [
    "AID1798",
    "AID1843",
    "AID2258",
    "AID2689",
    "AID435008",
    "AID435034",
    "AID463087",
    "AID485290",
    "AID488997",
]

DATASET_PREFIX = "WELQRATE"
SEEDS = tuple(range(1, 6))


def canonicalize_smiles(smiles: str) -> str | None:
    """Return canonical SMILES or None if the input is invalid."""
    if pd.isna(smiles) or not isinstance(smiles, str) or not smiles.strip():
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None


def ensure_extracted_root(zip_or_dir: Path, extract_dir: Path) -> Path:
    """Return a directory containing the WelQrate content.

    If `zip_or_dir` is a ZIP, extract to `extract_dir` (clears stale partials if needed).
    If it's a directory, return it directly.
    """
    if zip_or_dir.is_dir():
        return zip_or_dir

    if zip_or_dir.suffix.lower() == ".zip":
        extract_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Extracting ZIP %s to %s", zip_or_dir, extract_dir)
        with zipfile.ZipFile(zip_or_dir, "r") as zf:
            zf.extractall(extract_dir)
        return extract_dir

    raise FileNotFoundError(
        f"Unsupported path: {zip_or_dir}. Provide a .zip or an extracted directory."
    )


def locate_welqrate_dirs(root_dir: Path) -> tuple[Path, Path]:
    """Locate standard_formats and split/scaffold directories under root.

    Handles archives that add an extra top-level folder (e.g., WelQrate/...).
    """
    # 1) Direct paths
    std_direct = root_dir / "standard_formats"
    sca_direct = root_dir / "split" / "scaffold"
    if std_direct.is_dir() and sca_direct.is_dir():
        return std_direct, sca_direct

    # 2) Nested path: look for a single subdir that contains both
    for sub in root_dir.iterdir():
        if sub.is_dir():
            std = sub / "standard_formats"
            sca = sub / "split" / "scaffold"
            if std.is_dir() and sca.is_dir():
                return std, sca

    raise FileNotFoundError(
        "Could not locate required directories under extracted root. "
        f"Looked for 'standard_formats' and 'split/scaffold' under: {root_dir}"
    )


def read_target_from_standard_formats(standard_dir: Path, target: str) -> pd.DataFrame:
    """Read actives and inactives CSVs for a target and return a combined DataFrame.

    The function keeps auxiliary columns when present (CID, InChI, activity_value, etc.).
    Adds a binary column named exactly as `target` with values 1 for actives and 0 for inactives.
    """
    actives_path = standard_dir / f"{target}_actives.csv"
    inactives_path = standard_dir / f"{target}_inactives.csv"

    if not actives_path.exists() or not inactives_path.exists():
        raise FileNotFoundError(
            f"Missing CSVs for {target}: {actives_path} or {inactives_path}"
        )

    df_a = pd.read_csv(actives_path)
    df_i = pd.read_csv(inactives_path)

    # Normalize column names (strip whitespace)
    df_a.columns = [c.strip() for c in df_a.columns]
    df_i.columns = [c.strip() for c in df_i.columns]

    # Add target label
    df_a[target] = 1
    df_i[target] = 0

    df = pd.concat([df_a, df_i], ignore_index=True, sort=False)

    # Validate SMILES presence
    if "SMILES" not in df.columns:
        raise ValueError(f"CSV files for {target} must include a 'SMILES' column")

    return df


def process_target_with_canonicalization(
    df_raw: pd.DataFrame, target: str
) -> tuple[pd.DataFrame, list[int]]:
    """Canonicalize SMILES and drop invalid; return processed df and indices removed.

    The returned dataframe index is reset to 0..n-1 and contains at least columns:
    - SMILES (canonical)
    - target (binary)
    Auxiliary columns (CID, InChI, activity_value, etc.) are preserved if present.
    """
    original_smiles = df_raw["SMILES"].tolist()

    canonical_smiles: list[Optional[str]] = []
    removed: list[int] = []

    for i, s in enumerate(tqdm(original_smiles, desc=f"Canonicalizing {target}")):
        c = canonicalize_smiles(s)
        canonical_smiles.append(c)
        if c is None:
            removed.append(i)

    df = df_raw.copy()
    df["_original_index"] = range(len(df_raw))
    df["SMILES"] = canonical_smiles
    # Drop invalid
    df = df.dropna(subset=["SMILES"]).reset_index(drop=True)

    logger.info(
        "Processed %s: %d -> %d SMILES (removed %d)",
        target,
        len(original_smiles),
        len(df),
        len(removed),
    )
    if removed:
        logger.debug("Removed SMILES indices: %s", sorted(removed)[:10])

    if len(df["_original_index"]) != len(set(df["_original_index"])):
        logger.error("Duplicate original indices detected after processing!")

    return df, removed


def inspect_split_object(obj: Any) -> dict[str, list[int]]:
    """Normalise a split dictionary to contain train/valid/test lists."""
    if not isinstance(obj, dict):
        raise TypeError(
            "Expected split file to load as a dict with train/valid/test keys"
        )

    def _as_list(value: Any) -> list[int]:
        if hasattr(value, "tolist"):
            value = value.tolist()
        return list(value)

    normalized: dict[str, list[int]] = {}
    for key, alias in (
        ("train", "train"),
        ("valid", "valid"),
        ("validation", "valid"),
        ("val", "valid"),
        ("test", "test"),
    ):
        if key in obj:
            normalized[alias] = _as_list(obj[key])

    if "train" not in normalized or "test" not in normalized:
        raise ValueError("Split file must contain 'train' and 'test' entries")

    return normalized


def load_scaffold_split(
    scaffold_dir: Path, target: str, scaffold: str, seed: int
) -> dict[str, list[int]]:
    """Load scaffold split for a given target, scaffold type (2d/3d) and seed (1..5)."""
    if torch is None:
        raise RuntimeError(
            "torch is required to load WelQrate .pt split files. Please install torch."
        )

    fname = f"{target}_{scaffold}_scaffold_seed{seed}.pt"
    pt_path = scaffold_dir / fname
    if not pt_path.exists():
        raise FileNotFoundError(f"Split file not found: {pt_path}")

    obj = torch.load(pt_path, map_location="cpu")
    return inspect_split_object(obj)


def map_ids_to_processed_indices(
    df_processed: pd.DataFrame, ids: list[int]
) -> list[int]:
    """Map split indices (based on original ordering) to positions after filtering."""
    if "_original_index" not in df_processed.columns:
        raise ValueError(
            "Processed dataframe is missing '_original_index' helper column"
        )

    # Show range of original indices
    min_idx = df_processed["_original_index"].min()
    max_idx = df_processed["_original_index"].max()
    logger.info(
        "Mapping %d indices to processed data (original index range: %d..%d, %d rows)",
        len(ids),
        min_idx,
        max_idx,
        len(df_processed),
    )

    origin_to_new = dict(zip(df_processed["_original_index"], df_processed.index))

    mapped: list[int] = []
    missing_indices = []
    for idx in ids:
        idx = int(idx)
        if idx not in origin_to_new:
            missing_indices.append(idx)
            continue
        mapped.append(origin_to_new[idx])

    if missing_indices:
        missing_percent = 100.0 * len(missing_indices) / len(ids)
        logger.warning(
            "Could not map %d/%d (%.1f%%) original indices to processed data",
            len(missing_indices),
            len(ids),
            missing_percent,
        )
        # Show sample missing indices
        logger.debug("Sample missing indices: %s", sorted(missing_indices)[:10])

    return mapped


def save_splits(
    splits: dict[str, np.ndarray],
    splits_dir: Path,
    target: str,
    dataset_prefix: str,
    seed: int | None = None,
) -> None:
    """Save split indices to files, optionally prefixing with a seed label."""
    splits_dir.mkdir(parents=True, exist_ok=True)
    for split_name, indices in splits.items():
        prefix = f"seed{seed}_" if seed is not None else ""
        split_path = (
            splits_dir / f"{prefix}{dataset_prefix}_{target}.{split_name}_idx.npy"
        )
        np.save(split_path, indices)
        logger.info("Saved %s split to %s", split_name, split_path)


def process_welqrate_dataset(
    zip_path: Path,
    output_dir: Optional[Path] = None,
    splits_dir: Optional[Path] = None,
    cache_dir: Optional[Path] = None,
    scaffold: str = "2d",
) -> None:
    """Main function to process WelQrate dataset from a local source.

    Parameters
    ----------
    zip_path : Path
        Path to WelQrate.zip or to an extracted directory containing folders
        standard_formats/ and split/.
    output_dir : Optional[Path]
        Where to save processed Parquet files. Defaults to cache_dir.
    splits_dir : Optional[Path]
        Where to save train/test indices. Defaults to output_dir / "splits".
    cache_dir : Optional[Path]
        Temporary directory to extract ZIP if needed.
    scaffold : str
        "2d" or "3d" scaffold split selection.
    """
    if scaffold not in {"2d", "3d"}:
        raise ValueError("scaffold must be '2d' or '3d'")

    # Resolve directories
    if cache_dir is None:
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

    root_dir = ensure_extracted_root(Path(zip_path), cache_dir / "welqrate_extracted")

    standard_dir, scaffold_dir = locate_welqrate_dirs(root_dir)

    logger.info("Processing WelQrate from %s", root_dir)
    logger.info("Output directory: %s", output_dir)
    logger.info("Splits directory: %s", splits_dir)

    for target in tqdm(AVAILABLE_TARGETS, desc="Processing targets"):
        # 1) Read input CSVs
        df_raw = read_target_from_standard_formats(standard_dir, target)

        # 2) Canonicalize
        df_proc, _removed = process_target_with_canonicalization(df_raw, target)

        # 3) Save processed parquet (only SMILES + target)
        out_path = output_dir / f"{DATASET_PREFIX}_{target}.parquet"
        df_out = df_proc[["SMILES", target]]
        df_out.to_parquet(out_path, index=False)
        logger.info("Saved processed dataset to %s", out_path)

        # 4) Load each seed split and map to indices
        def split_for_seed(sd: int) -> tuple[np.ndarray, np.ndarray]:
            split_raw = load_scaffold_split(
                scaffold_dir, target, scaffold=scaffold, seed=sd
            )
            # Combine train + valid into train if valid present
            # Note: inspect_split_object normalizes "val"/"validation" to "valid"
            train_ids: list[int] = list(split_raw.get("train", []))
            if "valid" in split_raw:
                train_ids += list(split_raw.get("valid", []))
            test_ids: list[int] = list(split_raw.get("test", []))

            train_idx = np.array(
                sorted(map_ids_to_processed_indices(df_proc, train_ids)), dtype=int
            )
            test_idx = np.array(
                sorted(map_ids_to_processed_indices(df_proc, test_ids)), dtype=int
            )
            return train_idx, test_idx

        for sd in SEEDS:
            train_idx, test_idx = split_for_seed(sd)
            save_splits(
                {"train": train_idx, "test": test_idx},
                splits_dir,
                target,
                DATASET_PREFIX,
                seed=sd,
            )
            logger.info(
                "Seed %d splits for %s saved (train=%d, test=%d)",
                sd,
                target,
                len(train_idx),
                len(test_idx),
            )

    logger.info("=" * 60)
    logger.info("WelQrate processing completed!")
    logger.info("Processed datasets saved to: %s", output_dir)
    logger.info("  - Format: %s_<target>.parquet", DATASET_PREFIX)
    logger.info("Splits saved to: %s", splits_dir)
    logger.info("  - Format: seed{n}_%s_<target>.train_idx.npy", DATASET_PREFIX)
    logger.info("  - Format: seed{n}_%s_<target>.test_idx.npy", DATASET_PREFIX)
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Process WelQrate dataset from a local ZIP or directory, canonicalize SMILES, "
            "and export per-target Parquet files with scaffold splits."
        )
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        required=True,
        help="Path to WelQrate.zip or an extracted folder containing standard_formats/ and split/",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save processed datasets (default: sklearn cache)",
    )
    parser.add_argument(
        "--splits-dir",
        type=Path,
        help="Directory to save splits (default: output_dir / 'splits')",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        help="Directory for temporary files and extraction (default: sklearn cache)",
    )
    parser.add_argument(
        "--scaffold",
        type=str,
        default="2d",
        choices=["2d", "3d"],
        help="Type of scaffold split to use (2d or 3d). Default: 2d",
    )
    args = parser.parse_args()

    process_welqrate_dataset(
        zip_path=args.zip_path,
        output_dir=args.output_dir,
        splits_dir=args.splits_dir,
        cache_dir=args.cache_dir,
        scaffold=args.scaffold,
    )
