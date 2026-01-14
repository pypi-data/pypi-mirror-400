"""Script to canonicalize SMILES strings in dataset files located in a directory.

Given a path to a directory containing dataset files (e.g. `*.csv`, `*.parquet`),
the script walks through the files, canonicalizes SMILES strings using RDKit, and
overwrites the files with the canonicalized values.
"""

import argparse
import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
from rdkit import Chem
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".csv", ".parquet")


def canonicalize_smiles(smiles: str) -> Optional[str]:
    """Return canonical SMILES or None if the input is invalid."""
    if pd.isna(smiles) or not isinstance(smiles, str) or not smiles.strip():
        return None

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None


def detect_smiles_column(columns: Iterable[str]) -> Optional[str]:
    """Find a column named like SMILES (case-insensitive)."""
    for column in columns:
        if column.lower() == "smiles":
            return column
    return None


def read_dataset(path: Path) -> pd.DataFrame:
    """Read a dataset from CSV or Parquet."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path, engine="pyarrow")
    raise ValueError(f"Unsupported file type: {path}")


def write_dataset(df: pd.DataFrame, path: Path) -> None:
    """Write a dataset to CSV or Parquet."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
        return
    if suffix == ".parquet":
        df.to_parquet(path, index=False, engine="pyarrow")
        return
    raise ValueError(f"Unsupported file type: {path}")


def canonicalize_file(
    path: Path,
    smiles_column: Optional[str] = None,
    *,
    remove_invalid: bool = True,
    show_progress: bool = True,
    dry_run: bool = False,
) -> tuple[int, int, list[int]]:
    """Canonicalize SMILES in a single dataset file.

    Returns
    -------
    tuple[int, int, list[int]]
        Tuple of (original_rows, invalid_count, removed_indices)
        removed_indices contains original 0-based indices of removed rows
    """
    df = read_dataset(path)
    column = smiles_column or detect_smiles_column(df.columns)
    if column is None:
        logger.warning("Skipping '%s': no SMILES column found", path)
        return 0, 0, []

    iterator = (
        tqdm(df[column], desc=f"Canonicalizing {path.name}", unit="SMILES")
        if show_progress
        else df[column]
    )

    canonical_smiles: list[Optional[str]] = []
    invalid_count = 0
    removed_indices: list[int] = []

    for idx, smiles in enumerate(iterator):
        canonical = canonicalize_smiles(smiles)
        if canonical is None:
            invalid_count += 1
            if remove_invalid:
                canonical_smiles.append(None)
                removed_indices.append(idx)
            else:
                canonical_smiles.append(smiles)  # Keep original if invalid
        else:
            canonical_smiles.append(canonical)

    original_rows = len(df)

    df[column] = canonical_smiles
    if remove_invalid:
        df = df[df[column].notna()]

    if dry_run:
        logger.info(
            "Dry run: '%s' would be updated (%d -> %d rows, %d invalid SMILES removed)",
            path,
            original_rows,
            len(df),
            invalid_count,
        )
    else:
        write_dataset(df, path)
        logger.info(
            "Canonicalized '%s' (%d -> %d rows, %d invalid SMILES removed)",
            path,
            original_rows,
            len(df),
            invalid_count,
        )

    return original_rows, invalid_count, removed_indices


def iter_dataset_files(
    base_dir: Path, extensions: Sequence[str], recursive: bool
) -> Iterable[Path]:
    """Yield dataset files from a directory filtered by extension."""
    if recursive:
        paths = base_dir.rglob("*")
    else:
        paths = base_dir.glob("*")

    normalized_exts = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions
    }

    for path in paths:
        if path.is_file() and path.suffix.lower() in normalized_exts:
            yield path


def canonicalize_directory(
    directory: Path,
    *,
    smiles_column: Optional[str],
    remove_invalid: bool,
    show_progress: bool,
    recursive: bool,
    extensions: Sequence[str],
    dry_run: bool,
    report_path: Optional[Path] = None,
) -> None:
    """Canonicalize SMILES for all files in a directory.

    Parameters
    ----------
    report_path : Optional[Path], default=None
        Path to save a JSON report of removed indices. If None, no report is saved.
        The report format is: {file_path: [list of removed 0-based indices]}
    """
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Provided path is not a directory: {directory}")

    files = list(iter_dataset_files(directory, extensions, recursive))
    if not files:
        logger.warning(
            "No dataset files found in '%s' with extensions: %s",
            directory,
            ", ".join(extensions),
        )
        return

    total_rows = 0
    total_invalid = 0
    removal_report: dict[str, list[int]] = {}

    for file_path in files:
        try:
            rows, invalid, removed_indices = canonicalize_file(
                file_path,
                smiles_column,
                remove_invalid=remove_invalid,
                show_progress=show_progress,
                dry_run=dry_run,
            )
            total_rows += rows
            total_invalid += invalid

            # Store removed indices for report (use relative path from directory)
            if removed_indices:
                try:
                    rel_path = file_path.relative_to(directory)
                except ValueError:
                    # If relative path fails, use absolute path
                    rel_path = file_path
                removal_report[str(rel_path)] = removed_indices

        except Exception as exc:
            logger.exception("Error processing '%s': %s", file_path, exc)

    # Save removal report if requested
    if report_path and removal_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(removal_report, f, indent=2)
        logger.info(
            "Removal report saved to '%s' (%d files with removed rows)",
            report_path,
            len(removal_report),
        )

    logger.info(
        "Done. Processed %d files (%d rows, %d invalid SMILES removed).",
        len(files),
        total_rows,
        total_invalid,
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Canonicalize SMILES strings in dataset files stored in a directory."
    )
    parser.add_argument(
        "directory", type=Path, help="Directory containing dataset files."
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=list(SUPPORTED_EXTENSIONS),
        help="File extensions to process (default: .csv .parquet).",
    )
    parser.add_argument(
        "--smiles-column",
        type=str,
        help="Name of the SMILES column (auto-detected by default).",
    )
    parser.add_argument(
        "--keep-invalid",
        action="store_true",
        help="Keep rows with invalid SMILES instead of removing them.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for dataset files recursively.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bars.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not overwrite files, just report would-be changes.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Path to save a JSON report of removed row indices (for updating splits).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    canonicalize_directory(
        directory=args.directory,
        smiles_column=args.smiles_column,
        remove_invalid=not args.keep_invalid,
        show_progress=not args.no_progress,
        recursive=args.recursive,
        extensions=args.extensions,
        dry_run=args.dry_run,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
